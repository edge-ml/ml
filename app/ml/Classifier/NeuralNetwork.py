from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Classifier import BaseClassififer
from bson.objectid import ObjectId
from app.internal.config import CLASSIFIER_STORE
import os

import tensorflow as tf

class NeuralNetwork(BaseClassififer):
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
        return "Neural Network Classifier"

    @staticmethod
    def get_description():
        return "Abstract wrapper for neural network classifier, not intended for actual use."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]
    
    def fit(self, X_train, y_train):
        raise NotImplementedError()

    def predict(self, X_test):
        raise NotImplementedError()
    
    def get_state(self):
        return {"data_id": self.data_id}

    def restore(self, dict):
        self.data_id = dict.state["data_id"]
        path = f'{CLASSIFIER_STORE}/{self.data_id}'
        self.model = tf.saved_model.load(path)

    def persist(self):
        self.data_id = ObjectId()
        path = f'{CLASSIFIER_STORE}/{self.data_id}'
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        model_path = os.path.join(path, 'tf_model.tf')
        tf.saved_model.save(self.model, model_path)
        return super().persist()
    
    def exportLite(self):
        path = f'../../{CLASSIFIER_STORE}/{self.data_id}'
        converter = tf.lite.TFLiteConverter.from_saved_model(path)
        tflite_model = converter.convert()
        return tflite_model