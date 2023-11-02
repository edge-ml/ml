
from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep
from app.ml.BaseConfig import BaseConfig

class BaseClassififer(AbstractPipelineStep):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.is_fit = False
        self.parameters = parameters


    def fit(self, X_train, y_train):
        raise NotImplementedError

    def predict(self, X_test):
        raise NotImplementedError
    