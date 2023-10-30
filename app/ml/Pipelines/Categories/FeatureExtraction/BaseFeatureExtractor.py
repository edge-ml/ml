from app.ml.BaseConfig import BaseConfig

class BaseFeatureExtractor(BaseConfig):

    def __init__(self, parameters):
        super().__init__(parameters)

    def extract_features(self):
        raise NotImplementedError()