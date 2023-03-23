from app.ml.Normalizer.Normalizer import Normalizer
import numpy as np
import json
from app.utils.jsonEncoder import JSONEncoder

class MinMaxNormalizer(Normalizer):

    def __init__(self, parameters):
        super().__init__(parameters)
        self.min = None
        self.max = None

    @staticmethod
    def get_name():
        return "MinMaxNormalizer"
    
    @staticmethod
    def config():
        return {"name": MinMaxNormalizer.get_name(), "parameters": {}}
    
    def fit_normalize(self, data):
        self.min = np.min(data, axis=0)
        self.max = np.max(data, axis=0)
        data = (data - self.min) / (self.max - self.min)
        return data

    def normalize(self, data):
        if self.min is None or self.max is None:
            raise Exception()
        return (data - self.min) / (self.max - self.min)
    
    def get_state(self):
        return {"name": MinMaxNormalizer.get_name(), "min": json.dumps(self.min, cls=JSONEncoder), "max": json.dumps(self.max, cls=JSONEncoder)}