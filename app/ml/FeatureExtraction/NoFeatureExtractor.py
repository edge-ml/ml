from app.ml.FeatureExtraction import BaseFeatureExtractor
import numpy as np


class NoFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "None"

    @staticmethod
    def get_desciption():
        return "Extracts no features and returns the raw time-series"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_description():
        return "Does not extract any feature and returns the time-series as is."

    def extract_features(self, windows, labels):
        return windows[:, 0, 1:, np.newaxis], labels
    
    def exportC(self):
        return ''