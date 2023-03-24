from app.ml.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor


FEATURE_EXTRACTORS = [SimpleFeatureExtractor, NoFeatureExtractor]

def get_feature_extractor_by_name(name):
    for ext in FEATURE_EXTRACTORS:
        if ext.get_name() == name:
            return ext
    raise KeyError(f"Feature extractor with name {name} not found")


FEATURES_CONFIG = [x.config() for x in FEATURE_EXTRACTORS]