"""Classifier of the audio pipeline (#100): a 1-D CNN over the log-mel frames
and one over the sensor window, each pooled over time, concatenated and
classified by a linear layer. Either branch may be absent (audio-only or
sensor-only models). The input is the packed feature row of
LogMelSensorExtractor; the layout is stored in the architecture."""
import numpy as np
import torch
from torch import nn

from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from app.utils.parameter_builder import ParameterBuilder

# (audio filters, audio blocks, sensor filters, sensor blocks)
SIZES = {
    "small": (16, 2, 16, 2),
    "medium": (32, 3, 16, 2),
    "large": (64, 4, 32, 3),
}


class _Branch(nn.Module):
    """(batch, steps, channels) -> (batch, features)"""

    def __init__(self, steps, channels, filters, blocks, kernel_size=5):
        super().__init__()
        layers = []
        for b in range(blocks):
            out = min(filters * 2 ** b, 256)
            layers += [nn.Conv1d(channels, out, kernel_size, padding=kernel_size // 2), nn.BatchNorm1d(out), nn.ReLU()]
            if steps >= 2:
                layers.append(nn.MaxPool1d(2))
                steps //= 2
            channels = out
        self.net = nn.Sequential(*layers)
        self.out_features = channels

    def forward(self, x):
        return torch.mean(self.net(x.permute(0, 2, 1)), dim=2)


class MultimodalNet(nn.Module):
    def __init__(self, arch):
        super().__init__()
        layout = arch["layout"]
        self.audio = layout.get("audio")
        self.sensors = layout.get("sensors")
        width = 0
        if self.audio:
            self.audio_branch = _Branch(self.audio["frames"], self.audio["mels"], arch["audio_filters"], arch["audio_blocks"])
            width += self.audio_branch.out_features
        if self.sensors:
            self.sensor_branch = _Branch(self.sensors["samples"], self.sensors["channels"], arch["sensor_filters"], arch["sensor_blocks"])
            width += self.sensor_branch.out_features
        self.dropout = nn.Dropout(arch["dropout"])
        self.head = nn.Linear(width, arch["num_classes"])

    def forward(self, x):
        parts = []
        if self.audio:
            a = self.audio
            start = a["offset"]
            parts.append(self.audio_branch(x[:, start: start + a["frames"] * a["mels"]].reshape(-1, a["frames"], a["mels"])))
        if self.sensors:
            s = self.sensors
            start = s["offset"]
            parts.append(self.sensor_branch(x[:, start: start + s["samples"] * s["channels"]].reshape(-1, s["samples"], s["channels"])))
        h = parts[0] if len(parts) == 1 else torch.cat(parts, dim=1)
        return self.head(self.dropout(h))


class TorchMultimodalCNN(TorchNeuralNetwork):

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self._layout = None

    @staticmethod
    def get_name():
        return "PyTorch Audio & Sensor CNN"

    @staticmethod
    def get_description():
        return ("Convolutional network for sound, sensors or both: one branch learns from the spectrogram, one from "
                "the sensor window, and their findings are combined. Exports to smartphones, the browser and PyTorch.")

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_selection("size", "Model size", "Larger models can learn more, but need more data and take longer to train and run.",
                         list(SIZES), "medium", required=True, is_advanced=False)
        pb.add_number("epochs", "Training Epochs", "Number of passes over the training data.", 1, 500, 30, 1)
        pb.add_number("learning_rate", "Learning Rate", "Learning rate of the Adam optimizer.", 0.00001, 0.1, 0.001, 0.00001, True, True)
        pb.add_number("batch_size", "Batch Size", "Number of windows per training batch.", 4, 512, 32, 1)
        pb.add_number("dropout", "Dropout", "Dropout probability applied before the final layer during training.", 0, 0.9, 0.2, 0.05)
        return pb.parameters

    def fit_exec(self, data: PipelineContainer) -> PipelineContainer:
        if not data.layout:
            raise ValueError("The 'PyTorch Audio & Sensor CNN' needs the 'Log-mel spectrogram & sensors' feature extraction.")
        self._layout = data.layout
        return super().fit_exec(data)

    def build_arch(self, input_shape, num_classes):
        try:
            size = str(self.get_param_value_by_name("size") or "medium")
        except KeyError:
            size = "medium"
        audio_filters, audio_blocks, sensor_filters, sensor_blocks = SIZES.get(size, SIZES["medium"])
        return {
            "type": "multimodal_cnn",
            "input_shape": input_shape,
            "num_classes": num_classes,
            "layout": self._layout,
            "size": size,
            "audio_filters": audio_filters,
            "audio_blocks": audio_blocks,
            "sensor_filters": sensor_filters,
            "sensor_blocks": sensor_blocks,
            "dropout": self._get_param("dropout", 0.2, float),
        }

    @staticmethod
    def build_model(arch):
        return MultimodalNet(arch)

    def predict(self, X_test):
        # in batches: the conv activations of every window at once can be large
        X = np.asarray(X_test, dtype=np.float32)
        self.model.eval()
        out = []
        with torch.no_grad():
            for b in range(0, len(X), 512):
                out.append(torch.argmax(self.model(torch.from_numpy(X[b:b + 512])), dim=-1).numpy())
        return np.concatenate(out) if out else np.zeros(0, dtype=np.int64)
