
from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.BaseConfig import BaseConfig

class BaseClassififer(AbstractPipelineOption):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.is_fit = False
        self.parameters = parameters


    def fit(self, X_train, y_train):
        raise NotImplementedError

    def predict(self, X_test):
        raise NotImplementedError
    