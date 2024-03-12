from ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator
from ml.Pipelines.Categories.Windowing import WINDOWING_CATEGORY
from ml.Pipelines.AutoML import AUTOMLCLASSIFIER_CATEGORY
from ml.Pipelines.Categories.Evaluation import EVALUATION_CATEGORY
from ml.Pipelines.Categories.Common import COMMON_CATEGORY
from ml.Pipelines.Categories.Normalizer import NORMALIZER_CATEGORY
from ml.Pipelines.Versioning import Version


# @Version(1,0,0)
class AutoMLClassificationPipeline(AbstractPipeLineCreator):

    @classmethod
    def get_name(cls):
        return "AutoML Classification Pipeline"#
    
    @classmethod
    def get_description(cls):
        return "AutoML to automatically optimize your classification pipeline using NAS."
    
    @staticmethod
    def get_categories():
        return [WINDOWING_CATEGORY, NORMALIZER_CATEGORY, AUTOMLCLASSIFIER_CATEGORY, EVALUATION_CATEGORY]