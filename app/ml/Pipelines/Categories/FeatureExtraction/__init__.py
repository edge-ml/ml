from app.ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor
from app.ml.Pipelines.Categories.FeatureExtraction.FFTFeatureExtractor import FFTFeatureExtractor
from app.ml.Pipelines.Abstract.AbstractPipelineCategory import PipelineCategory
from typing import List

# FEATURE_EXTRACTORS : List[BaseFeatureExtractor] = [SimpleFeatureExtractor, NoFeatureExtractor, FFTFeatureExtractor]
FEATURE_EXTRACTORS : List[BaseFeatureExtractor] = [SimpleFeatureExtractor]

def get_feature_extractor_by_name(name):
    for ext in FEATURE_EXTRACTORS:
        if ext.get_name() == name:
            return ext
    raise KeyError(f"Feature extractor with name {name} not found")


FEATURES_CONFIG = [x.get_train_config() for x in FEATURE_EXTRACTORS]

FEATUREEXTRACTION_CATEGORY = PipelineCategory("Feature extraction", "The features to be extracted", FEATURES_CONFIG)