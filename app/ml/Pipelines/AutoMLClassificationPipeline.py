from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator
from app.ml.Pipelines.Categories.Windowing import WINDOWING_CATEGORY
from app.ml.Pipelines.AutoML import AUTOMLCLASSIFIER_CATEGORY
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CATEGORY
from app.ml.Pipelines.Categories.Common import COMMON_CATEGORY

class AutoMLClassificationPipeline(AbstractPipeLineCreator):

    @classmethod
    def get_name(cls):
        return "AutoML Classification Pipeline"#
    
    @classmethod
    def get_description(cls):
        return "AutoML to automatically optimize your classification pipeline using NAS."
    
    @staticmethod
    def get_categories():
        return [WINDOWING_CATEGORY, AUTOMLCLASSIFIER_CATEGORY, COMMON_CATEGORY, EVALUATION_CATEGORY]