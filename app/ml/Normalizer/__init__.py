from app.ml.Normalizer.BaseNormalizer import BaseNormalizer
from app.ml.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Normalizer.ZNormalizer import ZNormalizer
from typing import List

NORMALIZERS : List[BaseNormalizer]  = [MinMaxNormalizer, ZNormalizer]

def get_normalizer_by_name(name):
    for norm in NORMALIZERS:
        if (norm.get_name() == name):
            return norm
        

NORMALIZER_CONFIG = [x.get_train_config() for x in NORMALIZERS]