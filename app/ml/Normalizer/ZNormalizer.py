from app.ml.Normalizer.Normalizer import Normalizer
import numpy as np

class ZNormalizer(Normalizer):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.mean = None
        self.std = None

    @staticmethod
    def get_name():
        return "ZNormalizer"
    
    @staticmethod
    def config():
        return {"name": ZNormalizer.get_name(), "parameters": {}}

    def fit_normalize(self, data):
        self.mean = np.mean(data, axis=0)
        self.std = np.std(data, axis=0)
        data = (data - self.mean) / self.std
        return data

    def normalize(self, data):
        if self.mean is None or self.std is None:
            raise Exception()
        return (data - self.mean) / self.std
    
    def get_state(self):
        {"name": ZNormalizer.get_name(), "mean": self.mean, "std": self.std}