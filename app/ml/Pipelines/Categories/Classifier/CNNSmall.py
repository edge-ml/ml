from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier.NeuralNetwork import NeuralNetwork
import numpy as np
from app.ml.Pipelines.Categories.Classifier.utils import reshapeCNN

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

class CNNSmall(NeuralNetwork):
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None

    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        return pb.parameters

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
        
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        y_train_encoded = to_categorical(y_train, num_classes=num_classes)
        
        self.model.fit(X_train_reshaped, y_train_encoded, epochs=20)

    def predict(self, X_test):
        X_test_reshaped = reshapeCNN(X_test)
        prediction = self.model.predict(X_test_reshaped)
        prediction = np.argmax(prediction, axis=-1)
        return prediction