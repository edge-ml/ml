from app.codegen.inference.InferenceFormats import InferenceFormats
from app.ml.Classifier import NeuralNetwork
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

class DenseLarge(NeuralNetwork):
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None

    @staticmethod
    def get_name():
        return "Large Dense Neural Network"

    @staticmethod
    def get_description():
        return "Efficient classification neural architecture with dense feedforward layers for effective pattern recognition, eliminating the need for separate feature extraction."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

    def fit(self, X_train, y_train):
        num_classes = len(np.unique(y_train))
        self.model = Sequential([
            Dense(units=256, activation='relu', input_shape=(np.multiply(*X_train.shape[1:]), )),
            Dense(units=64, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        super().fit(X_train, y_train)