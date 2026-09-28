import numpy as np
from torch import nn

from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork


class TorchDense(TorchNeuralNetwork):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_number(
            "hidden_layers", "Hidden Layers", "Number of fully-connected hidden layers.",
            1, 5, 2, 1, True, False, False
        )
        pb.add_number(
            "hidden_units", "Hidden Units", "Number of units in each hidden layer.",
            4, 512, 32, 1, True, False, False
        )
        pb.add_number(
            "dropout", "Dropout", "Dropout probability applied after each hidden layer during training.",
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
        return "PyTorch Dense Neural Network"

    @staticmethod
    def get_description():
        return "Fully-connected feed-forward neural network built with PyTorch. Works on extracted features or raw windows and can be exported to smartphones via ExecuTorch (.pte)."

    def build_arch(self, input_shape, num_classes):
        return {
            "type": "dense",
            "input_shape": input_shape,
            "num_classes": num_classes,
            "hidden_layers": self._get_param("hidden_layers", 2, int),
            "hidden_units": self._get_param("hidden_units", 32, int),
            "dropout": self._get_param("dropout", 0.1, float),
        }

    @staticmethod
    def build_model(arch):
        in_features = int(np.prod(arch["input_shape"]))
        layers = [nn.Flatten()]
        for _ in range(arch["hidden_layers"]):
            layers.append(nn.Linear(in_features, arch["hidden_units"]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(arch["dropout"]))
            in_features = arch["hidden_units"]
        layers.append(nn.Linear(in_features, arch["num_classes"]))
        return nn.Sequential(*layers)
