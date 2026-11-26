"""Tests for training on audio (#100): decoding, the log-mel front-end, the
time-based windower, the feature packing and the per-channel normalizer.

Run from the ml/ directory: pytest tests/test_audio_training.py -v
"""

import os
import subprocess
import tempfile
import unittest
from types import SimpleNamespace

_TSDATA_DIR = tempfile.mkdtemp(prefix="edgeml_test_audio_")
_TEST_ENV = {
    "SECRET_KEY": "test",
    "API_URI": "http://localhost",
    "DATABASE_URI": "mongodb://localhost:27017",
    "AUTH_DATABASE_URI": "mongodb://localhost:27017",
    "CLASSIFIER_STORE": "CLASSIFIER_STORE",
    "TS_STORE_MECHANISM": "FS",
    "TSDATA": _TSDATA_DIR,
    "S3_URL": "http://localhost:9444",
    "S3_BUCKET_NAME": "test",
    "S3_ACCESS_KEY": "test",
    "S3_SECRET_KEY": "test",
    "S3_MODEL_BUCKET_NAME": "test-models",
    "FIRMWARE_COMPILE_URL": "http://localhost:3005/",
    "AUDIO_CACHE_DIR": os.path.join(_TSDATA_DIR, "audio-cache"),
}
for key, value in _TEST_ENV.items():
    os.environ.setdefault(key, value)

import numpy as np
import torch

from app.DataModels.dataset import MediaSeries
from app.DataProcessor.DataLoader import media
from app.DataProcessor.DataLoader.recordings import LabelIntervals, RecordingSource
from app.ml.PipelineExport.audio_ops import TorchLogMel, mel_filterbank, numpy_log_mel
from app.ml.Pipelines.Categories.FeatureExtraction.LogMelSensorExtractor import LogMelSensorExtractor
from app.ml.Pipelines.Categories.Normalizer.ChannelZNormalizer import ChannelZNormalizer
from app.ml.Pipelines.Categories.Windowing import SyncedTimeWindower as windowing
from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import SyncedTimeWindower, window_labels
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.utils.labels import UNLABELED_LABEL, window_majority_label
from app.utils.parameter_builder import ParameterBuilder

RATE = 16000


def params(cls, **values):
    """The option's default parameters with some values changed."""
    out = cls.get_parameters()
    for p in out:
        if p.parameter_name in values:
            p.value = values[p.parameter_name]
    return out


def labels(*intervals):
    return LabelIntervals(
        starts=np.array([float(s) for s, _, _ in intervals]),
        ends=np.array([float(e) for _, e, _ in intervals]),
        classes=np.array([c for _, _, c in intervals], dtype=np.int64),
    )


def source(audio_start=None, duration_ms=0, sensors=None, label_intervals=None, zero=None, media_id=None):
    """A recording source with in-memory sensors: sensors is a list of
    (times_ms, values) per channel."""
    sensors = sensors or []
    audio = None
    if audio_start is not None:
        audio = MediaSeries(_id=media_id or "0" * 24, kind="audio", name="mic", start=audio_start,
                            end=audio_start + duration_ms, durationMs=duration_ms)
    s = RecordingSource(
        dataset_id="d", meta={"subject": "a"},
        sensor_names=[f"s{i}" for i in range(len(sensors))],
        sensor_ids=[f"id{i}" for i in range(len(sensors))],
        sensor_spans=[(float(t[0]), float(t[-1])) for t, _ in sensors],
        sensor_periods_ms=[float(np.mean(np.diff(t))) for t, _ in sensors],
        conversions={}, audio=audio,
        labels=label_intervals if label_intervals is not None else labels(),
        zero_class=zero,
    )
    s._sensors = [(np.asarray(t, dtype=np.float64), np.asarray(v, dtype=np.float32)) for t, v in sensors]
    return s


class LogMelTest(unittest.TestCase):

    def test_filterbank_covers_the_spectrum_once(self):
        fb = mel_filterbank(RATE, 400, 40)
        self.assertEqual(fb.shape, (40, 201))
        self.assertTrue((fb >= 0).all())
        # neighbouring triangles add up to 1 between the first and last centre
        mid = fb.sum(axis=0)[20:180]
        np.testing.assert_allclose(mid, 1.0, atol=0.02)

    def test_torch_matches_numpy_rfft(self):
        rng = np.random.default_rng(0)
        t = np.arange(RATE) / RATE
        audio = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.05 * rng.standard_normal(RATE)
        ours = TorchLogMel()(torch.from_numpy(audio.astype(np.float32))[None])[0].numpy()
        ref = numpy_log_mel(audio)
        self.assertEqual(ours.shape, (98, 40))
        np.testing.assert_allclose(ours, ref, atol=1e-3)

    def test_tone_lands_in_its_band(self):
        t = np.arange(RATE) / RATE
        low = TorchLogMel()(torch.from_numpy(np.sin(2 * np.pi * 300 * t).astype(np.float32))[None])[0]
        high = TorchLogMel()(torch.from_numpy(np.sin(2 * np.pi * 4000 * t).astype(np.float32))[None])[0]
        self.assertLess(int(low.mean(0).argmax()), int(high.mean(0).argmax()))


class WindowLabelTest(unittest.TestCase):
    """window_labels must agree with the sample windower's rule applied to a
    1 kHz label track."""

    def brute(self, starts, window_ms, intervals, zero=None):
        out = []
        for s in starts:
            track = np.full(int(window_ms), UNLABELED_LABEL)
            for i, t in enumerate(np.arange(s, s + window_ms)):
                for a, b, c in intervals:
                    if a <= t <= b:
                        track[i] = c
                        break
                else:
                    if zero is not None:
                        track[i] = zero
            out.append(window_majority_label(track))
        return np.array(out)

    def test_matches_per_sample_rule(self):
        rng = np.random.default_rng(1)
        for trial in range(30):
            intervals, t = [], 0
            for _ in range(6):
                t += int(rng.integers(0, 400))
                length = int(rng.integers(50, 900))
                intervals.append((t, t + length, int(rng.integers(0, 3))))
                t += length + 1
            starts = np.arange(0, t, 137.0)
            for zero in (None, 3):
                got = window_labels(starts, 500, labels(*intervals), zero)
                np.testing.assert_array_equal(got, self.brute(starts, 500, intervals, zero), err_msg=f"trial {trial} zero {zero}")


class WindowerTest(unittest.TestCase):

    def setUp(self):
        self.pcm = (np.arange(10 * RATE) % 1000).astype(np.int16)
        self._load = media.load_audio
        media.load_audio = lambda media_id, rate: self.pcm

    def tearDown(self):
        media.load_audio = self._load

    def test_mixed_windows(self):
        t = np.arange(0, 10001, 20.0)  # 50 Hz
        src = source(audio_start=0, duration_ms=10000,
                     sensors=[(t, t * 2), (t, -t)],
                     label_intervals=labels((0, 4999, 0), (5000, 10000, 1)))
        w = SyncedTimeWindower(params(SyncedTimeWindower, window_ms=1000, stride_ms=500))
        out = w.fit_exec(PipelineContainer([src], None, None))
        self.assertEqual(w.sensor_rate, 50.0)
        self.assertEqual((w.sensor_samples, w.audio_samples), (50, 16000))
        self.assertEqual(len(out.data), 19)
        # window 9 (4500-5500 ms) is half and half: a tie goes to the lower
        # class, as in window_majority_label
        self.assertEqual(out.labels.tolist(), [0] * 10 + [1] * 9)
        sensors = w.sensors_for(out.data)
        self.assertEqual(sensors.shape, (19, 50, 2))
        np.testing.assert_allclose(sensors[1, :, 0], (500 + np.arange(50) * 20) * 2)
        np.testing.assert_allclose(sensors[1, :, 1], -(500 + np.arange(50) * 20))
        audio = w.audio_for(out.data)
        np.testing.assert_allclose(audio[1], self.pcm[8000:24000] / 32768.0)
        self.assertEqual(out.meta[0], {"subject": "a"})
        w.release()
        with self.assertRaises(windowing.WindowingError):
            windowing.windower_for(out.data)

    def test_audio_only_and_offset_start(self):
        # recording starts 2 s into the dataset; labels before it are not windowed
        src = source(audio_start=2000, duration_ms=3000, label_intervals=labels((0, 2999, 0), (3000, 10000, 1)))
        w = SyncedTimeWindower(params(SyncedTimeWindower, window_ms=1000, stride_ms=1000))
        out = w.fit_exec(PipelineContainer([src], None, None))
        self.assertEqual(out.labels.tolist(), [0, 1, 1])
        self.assertEqual(out.data[:, 2].tolist(), [0, 16000, 32000])
        self.assertEqual(w.export_inputs(), [{"name": "audio", "kind": "audio", "shape": [1, 16000], "sample_rate": 16000}])
        w.release()

    def test_sensor_only_drops_windows_beyond_a_channel(self):
        t1 = np.arange(0, 4001, 10.0)
        t2 = np.arange(0, 2501, 10.0)  # second channel stops early
        src = source(sensors=[(t1, t1), (t2, t2)], label_intervals=labels((0, 4000, 0)))
        w = SyncedTimeWindower(params(SyncedTimeWindower, window_ms=1000, stride_ms=500))
        out = w.fit_exec(PipelineContainer([src], None, None))
        # the span is cut to the shorter channel: windows at 0, 500, 1000, 1500 ms
        self.assertEqual(len(out.data), 4)
        self.assertEqual(w.sensor_rate, 100.0)
        self.assertIsNone(w.audio_rate)
        w.release()

    def test_window_cap(self):
        src = source(audio_start=0, duration_ms=10000, label_intervals=labels((0, 10000, 0)))
        w = SyncedTimeWindower(params(SyncedTimeWindower, window_ms=100, stride_ms=10))
        old = windowing.MAX_TRAIN_WINDOWS
        windowing.MAX_TRAIN_WINDOWS = 100
        try:
            with self.assertRaisesRegex(windowing.WindowingError, "at most 100"):
                w.fit_exec(PipelineContainer([src], None, None))
        finally:
            windowing.MAX_TRAIN_WINDOWS = old

    def test_state_round_trip(self):
        src = source(audio_start=0, duration_ms=3000, label_intervals=labels((0, 3000, 0)))
        w = SyncedTimeWindower(params(SyncedTimeWindower, window_ms=500, stride_ms=250, audio_rate_hz="8000"))
        w.fit_exec(PipelineContainer([src], None, None))
        restored = SyncedTimeWindower()
        restored.restore(SimpleNamespace(state=w.get_state(), parameters=w.parameters, input_shape=None, output_shape=None))
        self.assertEqual(restored.export_inputs(), [{"name": "audio", "kind": "audio", "shape": [1, 4000], "sample_rate": 8000}])
        w.release()


class FeatureTest(unittest.TestCase):

    def setUp(self):
        rng = np.random.default_rng(2)
        self.pcm = (rng.standard_normal(6 * RATE) * 3000).astype(np.int16)
        self._load = media.load_audio
        media.load_audio = lambda media_id, rate: self.pcm
        t = np.arange(0, 6001, 20.0)
        self.src = source(audio_start=0, duration_ms=6000, sensors=[(t, np.sin(t)), (t, 100 + 5 * np.cos(t))],
                          label_intervals=labels((0, 2999, 0), (3000, 6000, 1)))
        self.w = SyncedTimeWindower(params(SyncedTimeWindower, window_ms=1000, stride_ms=500))
        self.windows = self.w.fit_exec(PipelineContainer([self.src], None, None))

    def tearDown(self):
        media.load_audio = self._load
        self.w.release()

    def test_packing_and_layout(self):
        ext = LogMelSensorExtractor(LogMelSensorExtractor.get_parameters())
        out = ext.fit_exec(self.windows)
        self.assertEqual(out.layout, {"audio": {"offset": 0, "frames": 98, "mels": 40},
                                      "sensors": {"offset": 3920, "samples": 50, "channels": 2}, "size": 4020})
        self.assertEqual(out.data.shape, (len(self.windows.data), 4020))
        expected = numpy_log_mel(self.pcm[8000:24000] / 32768.0)
        np.testing.assert_allclose(out.data[1, :3920].reshape(98, 40), expected, atol=1e-3)
        np.testing.assert_allclose(out.data[1, 3920:].reshape(50, 2), self.w.sensors_for(self.windows.data[1:2])[0])
        # a split container (as the evaluators make) still finds the audio
        again = ext.exec(PipelineContainer(self.windows.data[3:5], self.windows.labels[3:5], None))
        np.testing.assert_allclose(again.data, out.data[3:5])

    def test_export_module_matches_training_features(self):
        ext = LogMelSensorExtractor(LogMelSensorExtractor.get_parameters())
        out = ext.fit_exec(self.windows)
        module = ext.torch_feature_module()
        rows = self.windows.data[2:3]
        packed = module(torch.from_numpy(self.w.sensors_for(rows)), torch.from_numpy(self.w.audio_for(rows)))
        np.testing.assert_allclose(packed.numpy(), out.data[2:3], atol=1e-4)

    def test_per_channel_normalizer(self):
        ext = LogMelSensorExtractor(LogMelSensorExtractor.get_parameters())
        feats = ext.fit_exec(self.windows)
        norm = ChannelZNormalizer()
        out = norm.fit_exec(feats)
        self.assertEqual(out.layout, feats.layout)
        sensors = out.data[:, 3920:].reshape(-1, 50, 2)
        np.testing.assert_allclose(sensors.mean(axis=(0, 1)), 0, atol=1e-4)
        np.testing.assert_allclose(sensors.std(axis=(0, 1)), 1, atol=1e-3)
        mels = out.data[:, :3920].reshape(-1, 98, 40)
        np.testing.assert_allclose(mels.mean(axis=(0, 1)), 0, atol=1e-3)
        # one value per band, repeated over the frames
        self.assertEqual(len(np.unique(norm.mean[:3920].reshape(98, 40)[:, 7])), 1)
        restored = ChannelZNormalizer()
        restored.restore(SimpleNamespace(state=norm.get_state(), parameters=[], input_shape=None, output_shape=None))
        np.testing.assert_allclose(restored.normalize(feats.data), out.data, atol=1e-5)


class DecodeTest(unittest.TestCase):
    """The formats the dataset-store accepts, made with the bundled ffmpeg."""

    def setUp(self):
        import imageio_ffmpeg

        self.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        self.dir = tempfile.mkdtemp(dir=_TSDATA_DIR)

    def make(self, name, *args):
        path = os.path.join(self.dir, name)
        subprocess.run([self.ffmpeg, "-v", "error", "-y", *args, path], check=True)
        return path

    def tone(self, seconds=1, rate=44100, channels=1):
        return ["-f", "lavfi", "-i", f"sine=frequency=1000:sample_rate={rate}:duration={seconds}", "-ac", str(channels)]

    def assert_tone(self, pcm, seconds=1, tolerance_ms=60):
        self.assertAlmostEqual(len(pcm) / RATE, seconds, delta=tolerance_ms / 1000)
        spectrum = np.abs(np.fft.rfft(pcm[2000:10000].astype(np.float64)))
        self.assertAlmostEqual(np.argmax(spectrum) * RATE / 8000, 1000, delta=10)

    def test_formats(self):
        cases = {
            "a.wav": self.tone(),
            "stereo.wav": self.tone(channels=2),
            "a.mp3": self.tone() + ["-c:a", "libmp3lame"],
            "a.ogg": self.tone() + ["-c:a", "libvorbis"],
            "a.flac": self.tone(),
            "a.m4a": self.tone() + ["-c:a", "aac"],
            "a.webm": self.tone(rate=48000) + ["-c:a", "libopus"],
        }
        for name, args in cases.items():
            with self.subTest(name):
                self.assert_tone(media.decode_file(self.make(name, *args), RATE))

    def test_video_sound_track(self):
        path = self.make("v.mp4", "-f", "lavfi", "-i", "color=size=64x64:duration=1", *self.tone(), "-c:v", "libx264", "-c:a", "aac", "-shortest")
        self.assert_tone(media.decode_file(path, RATE))

    def test_video_without_sound(self):
        path = self.make("silent.mp4", "-f", "lavfi", "-i", "color=size=64x64:duration=1", "-c:v", "libx264")
        with self.assertRaises(media.AudioDecodeError):
            media.decode_file(path, RATE)

    def test_load_from_store_is_cached(self):
        from app.internal.config import TSDATA  # set by whichever test module loaded first

        os.makedirs(os.path.join(TSDATA, "media"), exist_ok=True)
        media_id = "a" * 24
        src = self.make("stored.wav", *self.tone(seconds=2))
        os.replace(src, os.path.join(TSDATA, "media", media_id))
        first = media.load_audio(media_id, 8000)
        self.assertEqual(len(first), 16000)
        os.remove(os.path.join(TSDATA, "media", media_id))  # served from the cache now
        np.testing.assert_array_equal(media.load_audio(media_id, 8000), first)


    def test_concurrent_loads_of_one_recording(self):
        """Two trainings (threads of one worker) decoding the same recording at
        once once raced on one temporary file name."""
        from concurrent.futures import ThreadPoolExecutor
        from app.internal.config import TSDATA

        os.makedirs(os.path.join(TSDATA, "media"), exist_ok=True)
        media_id = "b" * 24
        src = self.make("concurrent.wav", *self.tone(seconds=2))
        os.replace(src, os.path.join(TSDATA, "media", media_id))
        with ThreadPoolExecutor(6) as pool:
            results = list(pool.map(lambda _: media.load_audio(media_id, 16000), range(6)))
        for pcm in results:
            self.assertEqual(len(pcm), 32000)
            np.testing.assert_array_equal(pcm, results[0])
        leftovers = [f for f in os.listdir(os.path.dirname(media._cache_path(media_id, 16000))) if f.endswith(".part")]
        self.assertEqual(leftovers, [])

if __name__ == "__main__":
    unittest.main()
