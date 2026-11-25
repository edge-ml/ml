"""Torch building blocks for audio models (#100), used both to compute the
training features and inside every exported model, so that training and the
deployed model compute exactly the same thing.

The spectrogram is computed with plain ops (a strided Conv1d with fixed
Hann-windowed cos/sin kernels, a power, a mel matmul and a log) instead of
torch.stft, which ExecuTorch/XNNPACK cannot run. Checked against a numpy
rfft reference in tests/test_audio_training.py.
"""
import numpy as np
import torch
from torch import nn

LOG_EPS = 1e-6


def hz_to_mel(f):
    return 2595.0 * np.log10(1.0 + np.asarray(f, dtype=np.float64) / 700.0)


def mel_to_hz(m):
    return 700.0 * (10 ** (np.asarray(m, dtype=np.float64) / 2595.0) - 1.0)


def mel_filterbank(sample_rate, n_fft, n_mels, fmin=0.0, fmax=None):
    """(n_mels, n_fft // 2 + 1) triangular filters, HTK mel scale."""
    fmax = float(fmax) if fmax else sample_rate / 2.0
    bins = n_fft // 2 + 1
    freqs = np.linspace(0.0, sample_rate / 2.0, bins)
    edges = mel_to_hz(np.linspace(hz_to_mel(fmin), hz_to_mel(fmax), n_mels + 2))
    fb = np.zeros((n_mels, bins), dtype=np.float32)
    for m in range(n_mels):
        lo, centre, hi = edges[m], edges[m + 1], edges[m + 2]
        rising = (freqs - lo) / max(centre - lo, 1e-9)
        falling = (hi - freqs) / max(hi - centre, 1e-9)
        fb[m] = np.maximum(0.0, np.minimum(rising, falling))
    return fb


def frame_count(samples, n_fft, hop):
    return 1 + (int(samples) - int(n_fft)) // int(hop)


class TorchLogMel(nn.Module):
    """(batch, samples) float audio in [-1, 1] -> (batch, frames, n_mels)."""

    def __init__(self, sample_rate=16000, n_fft=400, hop=160, n_mels=40, fmin=0.0, fmax=None):
        super().__init__()
        bins = n_fft // 2 + 1
        n = np.arange(n_fft)
        k = np.arange(bins)[:, None]
        window = 0.5 - 0.5 * np.cos(2 * np.pi * n / n_fft)  # periodic Hann
        cos = np.cos(2 * np.pi * k * n / n_fft) * window
        sin = -np.sin(2 * np.pi * k * n / n_fft) * window
        kernel = np.concatenate([cos, sin]).astype(np.float32)[:, None, :]
        self.register_buffer("kernel", torch.from_numpy(kernel))
        fb = mel_filterbank(sample_rate, n_fft, n_mels, fmin, fmax)
        self.register_buffer("mel", torch.from_numpy(np.ascontiguousarray(fb.T)))
        self.hop = int(hop)
        self.bins = bins

    def forward(self, audio):
        spec = nn.functional.conv1d(audio.unsqueeze(1), self.kernel, stride=self.hop)
        re = spec[:, : self.bins]
        im = spec[:, self.bins:]
        power = re * re + im * im
        return torch.log(torch.matmul(power.transpose(1, 2), self.mel) + LOG_EPS)


def numpy_log_mel(audio, sample_rate=16000, n_fft=400, hop=160, n_mels=40, fmin=0.0, fmax=None):
    """Reference implementation with numpy's rfft (tests only)."""
    fb = mel_filterbank(sample_rate, n_fft, n_mels, fmin, fmax).astype(np.float64)
    window = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n_fft) / n_fft)
    frames = frame_count(len(audio), n_fft, hop)
    out = np.zeros((frames, n_mels))
    for t in range(frames):
        segment = np.asarray(audio[t * hop: t * hop + n_fft], dtype=np.float64) * window
        out[t] = np.log(fb @ (np.abs(np.fft.rfft(segment)) ** 2) + LOG_EPS)
    return out
