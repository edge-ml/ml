from codegen.export_javascript import export_javascript
from codegen.inference.InferenceFormats import InferenceFormats
from utils.parameter_builder import ParameterBuilder
from ml.Pipelines.Categories.Classifier import BaseClassififer
from sklearn.tree import DecisionTreeClassifier
from micromlgen import port
import m2cgen as m2c
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans, SpectralClustering
import numpy as np
import copy
from ml.Pipelines.Categories.Classifier.utils import reshapeSklearn
from bson.objectid import ObjectId
from internal.config import CLASSIFIER_STORE
import pickle 
import os
from ml.BaseConfig import Platforms
from Deploy.Sklearn.exportC_decisionTree import convert
from StorageProvider import StorageProvider

class KMeansClassifier(BaseClassififer):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.data_id = None

    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
        pb.parameters = []
        return pb.parameters


    @staticmethod
    def get_name():
        return "K-Means Classifier"

    @staticmethod
    def get_description():
        return "K-Means Classifier for anomaly detection"

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

    # def export(self, platform: InferenceFormats, window_size, labels, timeseries, scaler):
    #     if platform == InferenceFormats.PYTHON:
    #         return m2c.export_to_python(self.clf)
    #     elif platform == InferenceFormats.C_EMBEDDED:
    #     #     return port(self.clf)
    #     # elif platform == InferenceFormats.C:
    #         return m2c.export_to_c(self.clf)
    #     elif platform == InferenceFormats.JAVASCRIPT:
    #         return export_javascript(self)
    #     elif platform == InferenceFormats.CPP:
    #         return convertMCU(self, window_size, labels, timeseries, scaler, language=McuLanguage.CPP)
    #     elif platform == InferenceFormats.C:
    #         return convertMCU(self, window_size, labels, timeseries, scaler, language=McuLanguage.C)
    #     else:
    #         print(platform)
    #         raise NotImplementedError

    def exportC(self):
        return convert(self.clf)

    # class methods
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.clf = KMeans() # TODO: Set the parameters for this classifier

    def fit(self, X_train, y_train):
        X_train_reshaped = reshapeSklearn(X_train)
        self.clf = KMeans(n_clusters=len(np.unique(y_train)))
        self.clf.fit(X_train_reshaped)

    def predict(self, X_test):
        X_train_reshaped = reshapeSklearn(X_test)
        return self.clf.predict(X_train_reshaped)

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
    
    def get_state(self):
        return {"data_id": self.data_id}

    def restore(self, dict):
        self.data_id = dict.state["data_id"]
        byte_clf = StorageProvider.load(self.data_id)
        self.clf = pickle.loads(byte_clf)

    def persist(self):
        self.data_id = ObjectId()
        byte_clf = pickle.dumps(self.clf)
        StorageProvider.save(self.data_id, byte_clf)
        return {**super().persist()}