from app.codegen.inference.InferenceFormats import InferenceFormats
from app.ml.Classifier import ConvolutionalNeuralNetwork
import numpy as np
from app.ml.Classifier.utils import reshapeCNN

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

class CNNSmall(ConvolutionalNeuralNetwork):
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None

    @staticmethod
    def get_name():
        return "Small Convolutional Neural Network"

    @staticmethod
    def get_description():
        return "Efficient classification neural architecture with dense feedforward layers for effective pattern recognition, eliminating the need for separate feature extraction."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

    def fit(self, X_train, y_train):
        num_classes = len(np.unique(y_train))
        X_train_reshaped = reshapeCNN(X_train)
        
        self.model = Sequential([
            Conv2D(64, kernel_size=(3, 3), padding="same", activation='relu', input_shape=X_train_reshaped.shape[1:]),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(64, kernel_size=(3, 3), padding="same", activation='relu'),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        super().fit(X_train, y_train)