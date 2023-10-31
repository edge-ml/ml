from app.codegen.export_javascript import export_javascript
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier import BaseClassififer
from sklearn.tree import DecisionTreeClassifier
import m2cgen as m2c
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import copy
from app.ml.Pipelines.Categories.Classifier.utils import reshapeSklearn
from bson.objectid import ObjectId
from app.internal.config import CLASSIFIER_STORE
import pickle
import os
from app.ml.BaseConfig import Platforms
from app.Deploy.Sklearn.exportC_decisionTree import convert
from app.StorageProvider import StorageProvider

from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep


class AutoMLClassifier(AbstractPipelineStep):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.data_id = None

    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []

        pb.add_number(
            "peak_mem_limit",
            "Peak Memory Limit",
            "The maximum allowed peak memory size.",
            3000,
            50000,
            None,
            1,
            False,
            False,
        )
        return pb.parameters


    @staticmethod
    def get_name():
        return "AutoML Classifier"

    @staticmethod
    def get_description():
        return "Uses neural architecture search to find a suitable classifier"

    @staticmethod
    def get_platforms():
        return []

    def exportC(self):
        return convert(self.clf)

    # class methods
    def __init__(self, parameters=[]):
        super().__init__(parameters)

    def fit(self, X_train, y_train):
        X_train_reshaped = reshapeSklearn(X_train)
        self.clf.fit(X_train_reshaped, y_train)

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
        return super().persist()