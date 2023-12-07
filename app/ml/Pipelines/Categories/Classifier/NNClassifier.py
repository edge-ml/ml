from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier import BaseClassififer
from sklearn.cluster import KMeans
import numpy as np
from app.ml.Pipelines.Categories.Classifier.utils import reshapeSklearn
from bson.objectid import ObjectId
from app.internal.config import CLASSIFIER_STORE
import pickle 
import os
from app.Deploy.Sklearn.exportC_decisionTree import convert

class NNClassifier(BaseClassififer):

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
        return "Neural network classifier"

    @staticmethod
    def get_description():
        return "Classify time-series using neural networks."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]

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
        path = f'{CLASSIFIER_STORE}/{self.data_id}'
        with open(path + "/clf.pkl", "rb") as f:
            self.clf = pickle.load(f)

    def persist(self):
        self.data_id = ObjectId()
        path = f'{CLASSIFIER_STORE}/{self.data_id}'
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        with open(path + "/clf.pkl", 'wb') as f:
            pickle.dump(self.clf, f)  
        return super().persist()