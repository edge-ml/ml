from ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator

from ml.Pipelines.Categories.Normalizer import NORMALIZER_CATEGORY
from ml.Pipelines.Categories.Classifier import CLASSIFIER_CATEGORY
from ml.Pipelines.Categories.Evaluation import EVALUATION_CATEGORY
from ml.Pipelines.Categories.Windowing import WINDOWING_CATEGORY
from ml.Pipelines.Categories.FeatureExtraction import FEATUREEXTRACTION_CATEGORY
from ml.Pipelines.Categories.Common import COMMON_CATEGORY

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