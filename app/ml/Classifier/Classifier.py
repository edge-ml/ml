

from app.codegen.inference import InferenceFormats
from app.internal.consts import SAMPLE_BASED_WINDOWING, TIME_BASED_WINDOWING
from app.utils.parameter_builder import ParameterBuilder

class Classifier:
    # static methods
    @staticmethod
    def get_hyperparameters():
        raise NotImplementedError()

    @staticmethod
    def get_name():
        return "Edge Model Base"

    @staticmethod
    def get_description():
        return "Basic model that defines hyperparameters. Predicts random results based on class probability."

    @staticmethod
    def get_platforms():
        return []
    
    @staticmethod
    def config():
        raise NotImplementedError()

    # class methods
    def __init__(self, hyperparameters=[]):
        self.is_fit = False
        self._hyperparameters = hyperparameters


    def fit(self, X_train, y_train):
        raise NotImplementedError

    def predict(self, X_test):
        raise NotImplementedError

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error

    def export(self, platform: InferenceFormats): # https://github.com/nok/sklearn-porter#estimators (maybe?)
        raise NotImplementedError

    @property
    def hyperparameters(self):
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, value):
        self._hyperparameters = value
        params = {x["name"]: x["value"] for x in self._hyperparameters}
        self.clf.set_params(**params)

    def get_state():
        raise NotImplementedError()