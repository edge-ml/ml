from app.ml.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor
from app.ml.FeatureExtraction.FFTFeatureExtractor import FFTFeatureExtractor
from typing import List

# FEATURE_EXTRACTORS : List[BaseFeatureExtractor] = [SimpleFeatureExtractor, NoFeatureExtractor, FFTFeatureExtractor]
FEATURE_EXTRACTORS : List[BaseFeatureExtractor] = [SimpleFeatureExtractor]

def get_feature_extractor_by_name(name):
    for ext in FEATURE_EXTRACTORS:
        if ext.get_name() == name:
            return ext
    raise KeyError(f"Feature extractor with name {name} not found")


FEATURES_CONFIG = [x.get_train_config() for x in FEATURE_EXTRACTORS]