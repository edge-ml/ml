from app.ml.Classifier.utils import reshapeCNN
from app.ml.Classifier import NeuralNetwork

from tensorflow.keras.utils import to_categorical
import tensorflow_model_optimization as tfmot

import numpy as np

import tensorflow as tf

class ConvolutionalNeuralNetwork(NeuralNetwork):
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None
        self.X_train_representative = None

    @staticmethod
    def get_name():
        return "Convolutional Neural Network Classifier"

    @staticmethod
    def get_description():
        return "Abstract wrapper for convolutional neural network classifier, not intended for actual use."
    
    def fit(self, X_train, y_train):
        num_classes = len(np.unique(y_train))
        X_train_reshaped = reshapeCNN(X_train)

        random_indices = np.random.choice(len(X_train), size=min(200, X_train_reshaped.shape[0]), replace=False)  
        self.X_train_representative = X_train_reshaped[random_indices]
        
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
        X_test_reshaped = reshapeCNN(X_test)
        prediction = self.model.predict(X_test_reshaped)
        prediction = np.argmax(prediction, axis=-1)
        return prediction