import torch
from torch import nn

from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork


class _ChannelsFirst(nn.Module):
    """(batch, window, channels) -> (batch, channels, window)"""

    def forward(self, x):
        return x.permute(0, 2, 1)


class _GlobalAvgPool1d(nn.Module):
    """(batch, channels, window) -> (batch, channels)"""

    def forward(self, x):
        return torch.mean(x, dim=-1)


class TorchCNN1D(TorchNeuralNetwork):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number(
            "conv_blocks", "Convolution Blocks", "Number of Conv1d + ReLU + MaxPool blocks.",
            1, 4, 2, 1, True, False, False
        )
        pb.add_number(
            "base_filters", "Base Filters", "Number of filters in the first convolution block. Doubles with each block.",
            4, 128, 16, 1, True, False, False
        )
        pb.add_number(
            "kernel_size", "Kernel Size", "Size of the 1D convolution kernel (odd values).",
            3, 11, 5, 2
        )
        pb.add_number(
            "dropout", "Dropout", "Dropout probability applied before the final layer during training.",
            0, 0.9, 0.1, 0.05
        )
        pb.add_number(
            "epochs", "Training Epochs", "Number of passes over the training data.",
            1, 500, 50, 1
        )
        pb.add_number(
            "learning_rate", "Learning Rate", "Learning rate of the Adam optimizer.",
            0.00001, 0.1, 0.001, 0.00001, True, True
        )
        pb.add_number(
            "batch_size", "Batch Size", "Number of windows per training batch.",
            4, 512, 32, 1
        )
        return pb.parameters

    @staticmethod
    def get_name():
        return "PyTorch 1D Convolutional Neural Network"

    @staticmethod
    def get_description():
        return "1D convolutional neural network built with PyTorch that learns patterns directly from raw time-series windows. Best used with the 'Raw Time-Series (Sensors only)' feature extraction. Can be exported to smartphones via ExecuTorch (.pte)."

    def build_arch(self, input_shape, num_classes):
        return {
            "type": "cnn1d",
            "input_shape": input_shape,
            "num_classes": num_classes,
            "conv_blocks": self._get_param("conv_blocks", 2, int),
            "base_filters": self._get_param("base_filters", 16, int),
            "kernel_size": self._get_param("kernel_size", 5, int),
            "dropout": self._get_param("dropout", 0.1, float),
        }

    @staticmethod
    def build_model(arch):
        # incoming windows are (batch, window, channels)
        length = int(arch["input_shape"][0])
        in_channels = int(arch["input_shape"][1])
        filters = int(arch["base_filters"])
        kernel_size = int(arch["kernel_size"])

        layers = [_ChannelsFirst()]
        for _ in range(arch["conv_blocks"]):
            layers.append(nn.Conv1d(in_channels, filters, kernel_size, padding="same"))
            layers.append(nn.ReLU())
            if length >= 2:
                layers.append(nn.MaxPool1d(2))
                length = length // 2
            in_channels = filters
            filters = min(filters * 2, 256)
        layers.append(_GlobalAvgPool1d())
        layers.append(nn.Dropout(arch["dropout"]))
        layers.append(nn.Linear(in_channels, arch["num_classes"]))
        return nn.Sequential(*layers)
