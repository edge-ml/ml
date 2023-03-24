from app.ml.FeatureExtraction import BaseFeatureExtractor
import numpy as np


class SimpleFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, hyperparameters=[]):
        self._hyperparameters = hyperparameters
        self._FEATURES = [np.sum, np.median, np.mean, np.std, np.var, np.max, lambda x : np.abs(np.max(x)), np.min, lambda x : np.abs(np.min(x))]

    @staticmethod
    def get_name():
        return "SimpleFeatureExtractor"

    @staticmethod
    def config():
        return {"name": SimpleFeatureExtractor.get_name(), "parameters": []}

    @staticmethod
    def get_platforms():
        raise NotImplementedError()

    @staticmethod
    def get_description():
        raise "Extracts simple features form the incomming time-series windows"

    @staticmethod
    def get_Hyperparameters():
        return []

    def persist(self):
        return {}

    def _extract_features(self, data):
        return np.array([f(data) for f in self._FEATURES])

    def extract_features(self, windows, labels):
        window_features = []
        for w in windows:
            stack = []
            for i in range(1, windows.shape[-1]):
                stack.append(self._extract_features(w[:, i]))
            window_features.append(np.stack(stack))

        return np.array(window_features), labels