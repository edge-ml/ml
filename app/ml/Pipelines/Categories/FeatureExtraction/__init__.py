from ml.Pipelines.Categories.FeatureExtraction.BaseFeatureExtractor import BaseFeatureExtractor
from ml.Pipelines.Categories.FeatureExtraction.SimpleFeatureExtractor import SimpleFeatureExtractor
from ml.Pipelines.Categories.FeatureExtraction.NoFeatureExtractor import NoFeatureExtractor
from ml.Pipelines.Categories.FeatureExtraction.FFTFeatureExtractor import FFTFeatureExtractor
from ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep
from typing import List

# FEATURE_EXTRACTORS : List[BaseFeatureExtractor] = [SimpleFeatureExtractor, NoFeatureExtractor, FFTFeatureExtractor]
FEATURE_EXTRACTORS : List[BaseFeatureExtractor] = [SimpleFeatureExtractor, NoFeatureExtractor]

def get_feature_extractor_by_name(name):
    for ext in FEATURE_EXTRACTORS:
        if ext.get_name() == name:
            return ext
    raise KeyError(f"Feature extractor with name {name} not found")


FEATUREEXTRACTION_CATEGORY = AbstractPipelineStep("Feature extraction", "The features to be extracted", FEATURE_EXTRACTORS)