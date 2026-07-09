"""Torch re-implementations of the python preprocessing steps.

These modules are composed with the trained classifier into a single exported
graph, so the mobile side only has to buffer raw sensor windows. Constants
(normalizer statistics) are registered as buffers and baked into the .pte.

Numerical parity with the numpy implementations is required — see
tests/test_torch_executorch.py.
"""

import numpy as np
import torch
from torch import nn


class TorchSimpleFeatures(nn.Module):
    """Torch equivalent of SimpleFeatureExtractor.

    Input:  (batch, window, channels) raw sensor values.
    Output: (batch, channels, 9) features in the exact order of
    SimpleFeatureExtractor._FEATURES:
    sum, median, mean, std, var, max, abs(max), min, abs(min).

    Note np.median averages the two middle values for even-sized windows,
    while torch.median returns the lower one — hence the topk-based median
    (topk is used instead of sort because the ExecuTorch portable kernels
    include aten::topk but not aten::sort).
    """

    def forward(self, x):
        x = x.permute(0, 2, 1)  # (batch, channels, window)
        n = x.shape[-1]

        smallest = torch.topk(x, n // 2 + 1, dim=-1, largest=False).values
        if n % 2 == 1:
            median = smallest[..., -1]
        else:
            median = (smallest[..., -2] + smallest[..., -1]) / 2.0

        total = torch.sum(x, dim=-1)
        mean = torch.mean(x, dim=-1)
        std = torch.std(x, dim=-1, unbiased=False)
        var = torch.var(x, dim=-1, unbiased=False)
        maximum = torch.max(x, dim=-1).values
        minimum = torch.min(x, dim=-1).values

        return torch.stack(
            [
                total,
                median,
                mean,
                std,
                var,
                maximum,
                torch.abs(maximum),
                minimum,
                torch.abs(minimum),
            ],
            dim=-1,
        )


class TorchMinMaxNormalize(nn.Module):
    """Torch equivalent of MinMaxNormalizer.normalize with baked statistics."""

    def __init__(self, min_values: np.ndarray, max_values: np.ndarray):
        super().__init__()
        self.register_buffer("min_values", torch.as_tensor(np.asarray(min_values, dtype=np.float32)))
        self.register_buffer("max_values", torch.as_tensor(np.asarray(max_values, dtype=np.float32)))

    def forward(self, x):
        return (x - self.min_values) / (self.max_values - self.min_values)


class TorchZNormalize(nn.Module):
    """Torch equivalent of ZNormalizer.normalize with baked statistics."""

    def __init__(self, mean: np.ndarray, std: np.ndarray):
        super().__init__()
        self.register_buffer("mean", torch.as_tensor(np.asarray(mean, dtype=np.float32)))
        self.register_buffer("std", torch.as_tensor(np.asarray(std, dtype=np.float32)))

    def forward(self, x):
        return (x - self.mean) / self.std
