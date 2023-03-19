from app.ml.Normalizer.MinMaxNormalizer import MinMaxNormalizer
from app.ml.Normalizer.ZNormalizer import ZNormalizer

NORMALIZERS = [MinMaxNormalizer, ZNormalizer]

def get_normalizer_by_name(name):
    for norm in NORMALIZERS:
        if (norm.get_name() == name):
            return norm