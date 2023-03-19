from app.ml.Normalizer.Normalizer import Normalizer
import numpy as np

class MinMaxNormalizer(Normalizer):

    def __init__(self, parameters):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "MinMaxNormalizer"
    
    def normalize(self, data):
        min = np.min(data, axis=0)
        max = np.max(data, axis=0)
        data = (data - min) / (max - min)
        settings = {"min": min, "max": max}
        return data, settings

    def normalize_with(self, data, settings):
        min = settings["min"]
        max = settings["max"]
        return (data - min) / (max - min)