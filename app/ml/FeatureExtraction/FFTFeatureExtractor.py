from app.ml.FeatureExtraction import BaseFeatureExtractor
import numpy as np
from app.Deploy.CPP.cPart import CPart
from app.utils.StringFile import StringFile
from scipy.fft import fft


class FFTFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "FFTFeatureExtractor"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_description():
        return "Extracts simple features form the incomming time-series windows"

    def _extract_features(self, data):
        return np.abs(fft(data))

    def extract_features(self, windows, labels):
        window_features = []
        for w in windows:
            stack = []
            for i in range(1, windows.shape[-1]):
                stack.append(self._extract_features(w[:, i]))
            window_features.append(np.stack(stack))
        return np.array(window_features), labels

    def exportC(self):
        raise NotImplementedError()