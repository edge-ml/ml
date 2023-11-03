from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
from app.ml.Pipelines.Abstract.AbstractPipelineStep import PipelineCategory
from typing import List

NORMALIZERS : List[BaseNormalizer]  = [MinMaxNormalizer, ZNormalizer]

def get_normalizer_by_name(name) -> BaseNormalizer:
    for norm in NORMALIZERS:
        if (norm.get_name() == name):
            return norm
        

NORMALIZER_CONFIG = [x.get_train_config() for x in NORMALIZERS]

NORMALIZER_CATEGORY = PipelineCategory("Normalizer", "Defines how data is normalized", NORMALIZER_CONFIG)