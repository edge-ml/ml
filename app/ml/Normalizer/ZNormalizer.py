from app.ml.Normalizer.Normalizer import Normalizer
import numpy as np

class ZNormalizer(Normalizer):

    def __init__(self, parameters):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "ZNormalizer"
    
    def normalize(self, data):
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        data = (data - mean) / std
        settings = {"mean": mean, "std": std}
        return data, settings

    def normalize_with(self, data, settings):
        mean = settings["mean"]
        std = settings["std"]
        return (data - mean) / std