from app.ml.BaseConfig import BaseConfig

class BaseFeatureExtractor(BaseConfig):

    def extract_features(self):
        raise NotImplementedError()