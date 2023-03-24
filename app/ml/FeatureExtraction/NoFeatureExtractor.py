from app.ml.FeatureExtraction import BaseFeatureExtractor
import numpy as np


class NoFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, hyperparameters=[]):
        self._hyperparameters = hyperparameters

    @staticmethod
    def get_name():
        return "None"

    @staticmethod
    def config():
        return {"name": NoFeatureExtractor.get_name(), "parameters": []}

    @staticmethod
    def get_platforms():
        raise NotImplementedError()

    @staticmethod
    def get_description():
        raise "Does not extract any feature and returns the time-series as is."

    @staticmethod
    def get_Hyperparameters():
        return []

    def persist(self):
        return {}

    def extract_features(self, windows, labels):
        return windows, labels