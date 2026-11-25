from app.ml.BaseConfig import Platforms
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
from app.ml.Pipelines.PipelineContainer import PipelineContainer
import numpy as np


class ChannelZNormalizer(ZNormalizer):
    """Z-normalization with one mean and std per sensor channel and per mel
    band, shared over the time steps of a window, instead of one per feature
    column. Stored expanded to one value per column, so it exports exactly like
    the ZNormalizer (TorchZNormalize)."""

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self._layout = None

    @staticmethod
    def get_name():
        return "Per-channel ZNormalizer"

    @staticmethod
    def get_description():
        return "Each sensor channel and each pitch band gets mean 0 and std 1, measured over all time steps."

    @staticmethod
    def get_platforms():
        return [Platforms.EXECUTORCH]

    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        self._layout = data.layout
        return super().fit_exec(data)

    def fit_normalize(self, data):
        data = np.asarray(data, dtype=np.float64)
        layout = self._layout
        if not layout:
            return super().fit_normalize(data)
        mean = np.zeros(data.shape[1])
        std = np.ones(data.shape[1])
        blocks = []
        if layout.get("audio"):
            a = layout["audio"]
            blocks.append((a["offset"], a["frames"], a["mels"]))
        if layout.get("sensors"):
            s = layout["sensors"]
            blocks.append((s["offset"], s["samples"], s["channels"]))
        for offset, steps, channels in blocks:
            part = data[:, offset: offset + steps * channels].reshape(len(data), steps, channels)
            mean[offset: offset + steps * channels] = np.tile(part.mean(axis=(0, 1)), steps)
            std[offset: offset + steps * channels] = np.tile(part.std(axis=(0, 1)), steps)
        self.mean = mean.astype(np.float32)
        self.std = std.astype(np.float32)
        return ((data - self.mean) / (self.std + 1e-8)).astype(np.float32)

    def normalize(self, data):
        return (super().normalize(np.asarray(data, dtype=np.float32))).astype(np.float32)
