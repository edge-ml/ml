from app.ml.BaseConfig import BaseConfig


class BaseNormalizer(BaseConfig):
    
    def __init__(self, parameters=...):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        raise NotImplementedError()
    
    def fit_normalize(self, data):
        raise NotImplementedError()

    def normalize(self, data):
        raise NotImplementedError()