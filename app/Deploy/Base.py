from app.ml.Normalizer import get_normalizer_by_name
from app.DataModels.model import Model
from app.ml.BaseConfig import Platforms

def deployModel(model: Model):
    normalizer = get_normalizer_by_name(model.model.normalizer.name)([])
    normalizer.restore(model.model.normalizer)
    normalizer.export(Platforms.C)

    