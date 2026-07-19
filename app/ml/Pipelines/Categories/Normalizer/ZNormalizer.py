from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.BaseConfig import Platforms
import numpy as np
import json
from app.utils.jsonEncoder import JSONEncoder

class ZNormalizer(BaseNormalizer):

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.mean = None
        self.std = None

    @staticmethod
    def get_name():
        return "ZNormalizer"

    @staticmethod
    def get_description():
        return "Data will have mean of 0 and std of 1"
    
    @staticmethod
    def config():
        return {"name": ZNormalizer.get_name(), "parameters": {}}

    @staticmethod
    def get_platforms():
        return [Platforms.EXECUTORCH]

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
        return {"name": ZNormalizer.get_name(), "mean": json.dumps(self.mean, cls=JSONEncoder), "std": json.dumps(self.std, cls=JSONEncoder)}

    def restore(self, config):
        self.mean = np.array(json.loads(config.state["mean"]))
        self.std = np.array(json.loads(config.state["std"]))
        super().restore(config)