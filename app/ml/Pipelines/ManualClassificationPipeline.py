from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator

from app.ml.Pipelines.Categories.Normalizer import NORMALIZER_CONFIG
from app.ml.Pipelines.Categories.Classifier import CLASSIFIER_CONFIG, classifierCategory
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CONFIG
from app.ml.Windowing import WIDNOWING_CONFIG
from app.ml.Pipelines.Categories.FeatureExtraction import FEATURES_CONFIG

class ManualClassificationPipeline(AbstractPipeLineCreator):

    @classmethod
    def get_name(cls):
        return "Manual Classification Pipeline"#
    
    @classmethod
    def get_description(cls):
        return "Classification algorithms."
    
    @staticmethod
    def get_categories():
        return [classifierCategory]