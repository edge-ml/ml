from app.utils.parameter_builder import ParameterBuilder
from enum import Enum

class EdgeModelPlatform(Enum):
    PYTHON = 'python'
    JAVASCRIPT = 'javascript'
    JAVA = 'java'
    C = 'c'

class EdgeModel:
    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = ParameterBuilder()
        pb.add_number(
            "window_size", "Window Size", "Sets the window size", 0, 60000, 100, 1, True
        )
        pb.add_number(
            "sliding_step",
            "Sliding Step",
            "Sets how many steps the sliding window will slide. If it's set less than the window size, the windows will overlap.",
            1,
            60000,
            50,
            1,
            True,
        )
        return pb.parameters

    @staticmethod
    def get_name():
        return "Edge Model Base"

    @staticmethod
    def get_description():
        return "Basic model that defines hyperparameters. Predicts random results based on class probability."

    @staticmethod
    def get_platforms():
        return []

    # class methods
    def __init__(self, hyperparameters={}):
        self.is_fit = False
        self._hyperparameters = hyperparameters

    def fit(self, X_train, y_train):
        print(self.clf.get_params())
        self.clf.fit(X_train, y_train)

    def predict(self, X_test):
        return self.clf.predict(X_test)

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error

    def export(platform: EdgeModelPlatform): # https://github.com/nok/sklearn-porter#estimators (maybe?)
        if platform == EdgeModelPlatform.JAVASCRIPT:
            return 'code for js'
        elif platform == EdgeModelPlatform.JAVA:
            return 'code for java'

    @property
    def hyperparameters(self):
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, value):
        self._hyperparameters = value
        self.clf.set_params(**self._hyperparameters)
