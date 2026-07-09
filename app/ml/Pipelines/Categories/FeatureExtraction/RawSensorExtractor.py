from app.ml.Pipelines.Categories.FeatureExtraction import BaseFeatureExtractor
import numpy as np


class RawSensorExtractor(BaseFeatureExtractor):
    """Passes the raw sensor values of each window to the classifier and drops
    the timestamp column. Unlike 'None', the resulting model only depends on
    values a device can provide at inference time, which is required for the
    smartphone (ExecuTorch) export."""

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    @staticmethod
    def get_name():
        return "Raw Time-Series (Sensors only)"

    @staticmethod
    def get_description():
        return "Passes the raw sensor values of each window to the classifier (drops the timestamp column). Use this for models that should run on smartphones (ExecuTorch export)."

    @staticmethod
    def get_platforms():
        return []

    def extract_features(self, windows):
        try:
            return np.asarray([np.asarray(w, dtype=np.float32)[:, 1:] for w in windows])
        except ValueError:
            raise Exception(
                "Raw Time-Series feature extraction requires equally sized windows. Please use sample-based windowing."
            )
