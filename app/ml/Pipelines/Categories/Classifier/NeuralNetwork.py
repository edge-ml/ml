from codegen.inference.InferenceFormats import InferenceFormats
from utils.parameter_builder import ParameterBuilder
from ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
from bson.objectid import ObjectId
from internal.config import CLASSIFIER_STORE
from dataLoader import DATASTORE
import tempfile


from io import BytesIO
import os

import tensorflow as tf
from tensorflow.keras.models import load_model, save_model

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
        return [InferenceFormats.PYTHON]
    
    def fit(self, X_train, y_train):
        raise NotImplementedError()

    def predict(self, X_test):
        raise NotImplementedError()
    
    def get_state(self):
        return {"data_id": self.data_id}
    
    def as_file(self):
        buffer = None
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join("model.keras")
            self.model.save(path)
            with open(path, "rb") as f:
                buffer = BytesIO(f.read())
        return {"name": f"{self.get_name()}.keras", "buffer": buffer}

    def restore(self, dict):
        self.data_id = dict.state["data_id"]

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "model.keras")
            binModel = DATASTORE.loadObj(id=str(self.data_id))
            with open(path, "wb") as f:
                f.write(binModel.read())
            self.model = load_model(path)

    def persist(self):
        self.data_id = ObjectId()
        with tempfile.TemporaryDirectory() as tmp:
            str_id = str(self.data_id)
            path = os.path.join(tmp, "model.keras")
            self.model.save(path)
            with open(path, "rb") as f:
                DATASTORE.saveObj(str_id, BytesIO(f.read()))
        return super().persist()


    
    def exportLite(self):
        path = f'../../{CLASSIFIER_STORE}/{self.data_id}'
        converter = tf.lite.TFLiteConverter.from_saved_model(path)
        tflite_model = converter.convert()
        return tflite_model