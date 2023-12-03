from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Classifier import NeuralNetwork
import numpy as np
from app.ml.Classifier.utils import reshapeSklearn

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
import tensorflow_model_optimization as tfmot

class DenseSmall(NeuralNetwork):
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None

    # static methods
    @staticmethod
    def get_name():
        return "Small Dense Neural Network"

    @staticmethod
    def get_description():
        return "Efficient classification neural architecture with dense feedforward layers for effective pattern recognition, eliminating the need for separate feature extraction."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

    def fit(self, X_train, y_train):
        num_classes = len(np.unique(y_train))
        X_train_reshaped = reshapeSklearn(X_train)

        random_indices = np.random.choice(len(X_train), size=min(200, X_train_reshaped.shape[0]), replace=False)  
        self.X_train_representative = X_train_reshaped[random_indices]
        
        self.model = Sequential([
            Dense(units=8, activation='relu', input_shape=(X_train_reshaped.shape[1], )),
            Dense(units=8, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        y_train_encoded = to_categorical(y_train, num_classes=num_classes)

        self.model.fit(X_train_reshaped, y_train_encoded, epochs=20)
    
        quantization_aware_training = next((param.value == 'True' for param in self.parameters if param.name == 'quantization_aware_training'), False)
        
        if quantization_aware_training:
            self.model = tfmot.quantization.keras.quantize_model(self.model)
            self.model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])
            self.model.fit(X_train_reshaped, y_train_encoded, epochs=1, validation_split=0.1)
        

    def predict(self, X_test):
        X_test_reshaped = reshapeSklearn(X_test)
        prediction = self.model.predict(X_test_reshaped)
        prediction = np.argmax(prediction, axis=-1)
        return prediction