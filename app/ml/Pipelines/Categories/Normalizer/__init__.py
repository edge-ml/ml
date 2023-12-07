from app.ml.Pipelines.Categories.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Pipelines.Categories.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Pipelines.Categories.Normalizer.ZNormalizer import ZNormalizer
from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep
from typing import List

NORMALIZERS : List[BaseNormalizer]  = [MinMaxNormalizer, ZNormalizer]

def get_normalizer_by_name(name) -> BaseNormalizer:
    for norm in NORMALIZERS:
        if (norm.get_name() == name):
            return norm
        

NORMALIZER_CATEGORY = AbstractPipelineStep("Normalizer", "Defines how data is normalized", NORMALIZERS)