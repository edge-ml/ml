"""Audio of recordings, for training on sound (#100).

Recordings are stored by the dataset-store as uploaded (MP4, WebM, MP3, WAV,
OGG, FLAC, M4A). They are decoded here with a static ffmpeg build (pip package
imageio-ffmpeg) to mono 16-bit PCM at the model's sample rate, and cached on
local disk, since several trainings usually use the same recordings.
"""
import os
import subprocess
import tempfile
import threading

import numpy as np

from app.internal.config import AUDIO_CACHE_DIR, AUDIO_CACHE_MAX_BYTES

_lock = threading.Lock()


class AudioDecodeError(Exception):
    pass


def _ffmpeg():
    try:
        import imageio_ffmpeg
    except ImportError as e:  # pragma: no cover - present in the image
        raise AudioDecodeError("Audio decoding is not available on this server (imageio-ffmpeg is not installed).") from e
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode_file(path, rate) -> np.ndarray:
    """Mono int16 samples of the first sound track of a file, at `rate` Hz.
    Stereo is averaged; ffmpeg resamples with a proper low-pass filter."""
    res = subprocess.run(
        [_ffmpeg(), "-v", "error", "-nostdin", "-i", path, "-vn", "-map", "0:a:0",
         "-ac", "1", "-ar", str(int(rate)), "-f", "s16le", "-"],
        capture_output=True,
        timeout=3600,
    )
    if res.returncode != 0:
        reason = res.stderr.decode(errors="ignore").strip().splitlines()
        raise AudioDecodeError(reason[-1] if reason else "ffmpeg could not decode the recording")
    return np.frombuffer(res.stdout, dtype="<i2").copy()


def _cache_path(media_id, rate):
    return os.path.join(AUDIO_CACHE_DIR, f"{media_id}_{int(rate)}.s16")


def _trim_cache():
    """Delete the least recently used decoded files beyond the size limit."""
    try:
        files = [os.path.join(AUDIO_CACHE_DIR, f) for f in os.listdir(AUDIO_CACHE_DIR) if f.endswith(".s16")]
    except FileNotFoundError:
        return
    files.sort(key=lambda f: os.stat(f).st_atime, reverse=True)
    total = 0
    for f in files:
        total += os.path.getsize(f)
        if total > AUDIO_CACHE_MAX_BYTES:
            try:
                os.remove(f)
            except OSError:
                pass


def load_audio(media_id, rate) -> np.ndarray:
    """Mono int16 samples of a stored recording at `rate` Hz (cached)."""
    from app.dataLoader import DATASTORE

    path = _cache_path(media_id, rate)
    if os.path.exists(path):
        os.utime(path)  # most recently used
        return np.fromfile(path, dtype="<i2")
    os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "recording")
        try:
            DATASTORE.load_media_to_file(str(media_id), src)
        except Exception as e:
            raise AudioDecodeError(f"The recording file could not be read from storage: {e}") from e
        pcm = decode_file(src, rate)
    part = f"{path}.{os.getpid()}.part"
    pcm.tofile(part)
    os.replace(part, path)  # both workers may decode the same file at once
    with _lock:
        _trim_cache()
    return pcm
