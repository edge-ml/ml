

from app.codegen.inference import InferenceFormats
from app.internal.consts import SAMPLE_BASED_WINDOWING, TIME_BASED_WINDOWING
from app.utils.parameter_builder import ParameterBuilder
from app.ml.BaseConfig import BaseConfig

class BaseClassififer(BaseConfig):

    def __init__(self, parameters):
        self.is_fit = False
        self.parameters = parameters


    def fit(self, X_train, y_train):
        raise NotImplementedError

    def predict(self, X_test):
        raise NotImplementedError
