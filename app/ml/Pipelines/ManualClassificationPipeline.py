from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator

from app.ml.Pipelines.Categories.Normalizer import NORMALIZER_CONFIG, NORMALIZER_CATEGORY
from app.ml.Pipelines.Categories.Classifier import CLASSIFIER_CONFIG, CLASSIFIER_CATEGORY
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CONFIG, EVALUATION_CATEGORY
from app.ml.Pipelines.Categories.Windowing import WIDNOWING_CONFIG, WINDOWING_CATEGORY
from app.ml.Pipelines.Categories.FeatureExtraction import FEATURES_CONFIG, FEATUREEXTRACTION_CATEGORY

class ManualClassificationPipeline(AbstractPipeLineCreator):

    @classmethod
    def get_name(cls):
        return "Manual Classification Pipeline"#
    
    @classmethod
    def get_description(cls):
        return "Create your own time-series classification pipeline by selecting each step and setting its hyperparameters."
    
    @staticmethod
    def get_categories():
        return [WINDOWING_CATEGORY, FEATUREEXTRACTION_CATEGORY, NORMALIZER_CATEGORY, CLASSIFIER_CATEGORY, EVALUATION_CATEGORY]