"""Features of the audio pipeline (#100): the log-mel spectrogram of each
window's audio and the window's sensor values, packed into one row per window
so evaluators, normalizers and the classifier handle them like any other
feature array. The layout (see `layout`) says which columns are which.

The spectrogram is computed by TorchLogMel, the same module every exported
model contains, so training and deployment see identical features.
"""
import numpy as np
import torch
from torch import nn

from app.ml.BaseConfig import Platforms
from app.ml.PipelineExport.audio_ops import TorchLogMel, frame_count
from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.utils.parameter_builder import ParameterBuilder

# windows per spectrogram batch, bounds the memory of the conv
_BATCH = 256


def make_layout(frames, mels, samples, channels):
    """Columns of a packed feature row: the spectrogram (frames, mels) first,
    then the sensors (samples, channels); either may be absent."""
    layout = {"audio": None, "sensors": None}
    offset = 0
    if frames:
        layout["audio"] = {"offset": 0, "frames": int(frames), "mels": int(mels)}
        offset = int(frames) * int(mels)
    if channels:
        layout["sensors"] = {"offset": offset, "samples": int(samples), "channels": int(channels)}
        offset += int(samples) * int(channels)
    layout["size"] = offset
    return layout


class _PackFeatures(nn.Module):
    """The extractor as a module for the exports:
    (raw_window (1, samples, channels)?, audio (1, samples)?) -> (1, F)."""

    def __init__(self, logmel, has_sensors, has_audio):
        super().__init__()
        self.logmel = logmel
        self.has_sensors = has_sensors
        self.has_audio = has_audio

    def pack(self, raw_window, audio):
        parts = []
        if self.has_audio:
            parts.append(torch.flatten(self.logmel(audio), 1))
        if self.has_sensors:
            parts.append(torch.flatten(raw_window, 1))
        return parts[0] if len(parts) == 1 else torch.cat(parts, dim=1)


class _PackAudio(_PackFeatures):
    def forward(self, audio):
        return self.pack(None, audio)


class _PackSensors(_PackFeatures):
    def forward(self, raw_window):
        return self.pack(raw_window, None)


class _PackBoth(_PackFeatures):
    def forward(self, raw_window, audio):
        return self.pack(raw_window, audio)


class LogMelSensorExtractor(BaseFeatureExtractor):

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.layout = None
        self.sample_rate = None
        self.n_fft = None
        self.hop = None
        self.n_mels = None
        self._logmel = None

    @staticmethod
    def get_name():
        return "Log-mel spectrogram & sensors"

    @staticmethod
    def get_description():
        return ("Turns the sound of each window into a log-mel spectrogram (how loud each pitch band is over time) "
                "and passes the sensor values on unchanged. The exported models compute the spectrogram themselves.")

    @staticmethod
    def get_platforms():
        return [Platforms.EXECUTORCH]

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number("n_mels", "Mel bands", "Number of pitch bands of the spectrogram.", 8, 128, 40, 1, True, False, True)
        pb.add_number("frame_ms", "Frame length (ms)", "Length of the sound slice each spectrogram column is computed from.", 10, 100, 25, 1, True, False, True)
        pb.add_number("hop_ms", "Frame step (ms)", "Time between spectrogram columns.", 5, 50, 10, 1, True, False, True)
        return pb.parameters

    def _param(self, name, default):
        try:
            value = self.get_param_value_by_name(name)
        except KeyError:
            return default
        return default if value in (None, "") else float(value)

    # -- fitting -----------------------------------------------------------
    def _configure(self, windower):
        self.sample_rate = int(windower.audio_rate) if windower.audio_rate else None
        frames = 0
        if self.sample_rate:
            self.n_mels = int(self._param("n_mels", 40))
            self.n_fft = int(round(self._param("frame_ms", 25) * self.sample_rate / 1000.0))
            self.hop = max(1, int(round(self._param("hop_ms", 10) * self.sample_rate / 1000.0)))
            frames = frame_count(windower.audio_samples, self.n_fft, self.hop)
            if frames < 1:
                raise ValueError("The window is shorter than one spectrogram frame. Use a longer window.")
        self.audio_samples = int(windower.audio_samples)
        self.layout = make_layout(frames, self.n_mels, windower.sensor_samples, len(windower.channels))
        self._logmel = None

    def logmel(self) -> TorchLogMel:
        if self._logmel is None:
            self._logmel = TorchLogMel(self.sample_rate, self.n_fft, self.hop, self.n_mels).eval()
        return self._logmel

    def extract_features(self, rows):
        from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import windower_for

        rows = np.asarray(rows)
        out = np.zeros((len(rows), self.layout["size"]), dtype=np.float32)
        if len(rows) == 0:
            return out
        windower = windower_for(rows)
        audio, sensors = self.layout["audio"], self.layout["sensors"]
        if audio:
            end = audio["frames"] * audio["mels"]
            with torch.no_grad():
                for b in range(0, len(rows), _BATCH):
                    batch = torch.from_numpy(windower.audio_for(rows[b:b + _BATCH]))
                    out[b:b + _BATCH, :end] = torch.flatten(self.logmel()(batch), 1).numpy()
        if sensors:
            out[:, sensors["offset"]:] = windower.sensors_for(rows).reshape(len(rows), -1)
        return out

    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import windower_for

        self._configure(windower_for(data.data))
        features = self.extract_features(data.data)
        self.input_shape = None
        self.output_shape = [int(features.shape[1])]
        return PipelineContainer(features, data.labels, data.meta, self.layout)

    def exec(self, data: PipelineContainer) -> PipelineContainer:
        return PipelineContainer(self.extract_features(data.data), data.labels, data.meta, self.layout)

    # -- persistence -------------------------------------------------------
    def get_state(self):
        return {"layout": self.layout, "sample_rate": self.sample_rate, "n_fft": self.n_fft,
                "hop": self.hop, "n_mels": self.n_mels, "audio_samples": getattr(self, "audio_samples", 0)}

    def restore(self, config):
        state = config.state or {}
        self.layout = state.get("layout")
        self.sample_rate = state.get("sample_rate")
        self.n_fft = state.get("n_fft")
        self.hop = state.get("hop")
        self.n_mels = state.get("n_mels")
        self.audio_samples = state.get("audio_samples") or 0
        self._logmel = None
        super().restore(config)

    # -- export ------------------------------------------------------------
    def torch_feature_module(self) -> nn.Module:
        """Module from the model inputs (raw_window first, then audio, as in
        SyncedTimeWindower.export_inputs) to the packed feature row."""
        has_audio = bool(self.layout and self.layout.get("audio"))
        has_sensors = bool(self.layout and self.layout.get("sensors"))
        logmel = TorchLogMel(self.sample_rate, self.n_fft, self.hop, self.n_mels) if has_audio else None
        cls = _PackBoth if has_audio and has_sensors else (_PackAudio if has_audio else _PackSensors)
        return cls(logmel, has_sensors, has_audio).eval()
