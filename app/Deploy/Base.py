from app.ml.Pipelines.Categories.Normalizer import get_normalizer_by_name
from app.DataModels.model import Model
from app.ml.BaseConfig import Platforms
from app.ml.Pipelines import getPipeline
from io import BytesIO
import zipfile

def downloadModel(model, platform: Platforms):
    pipeline = getPipeline(model)
    pipeline.export(model, platform)
    # zipFile = pipeline.generateModelData(platform)
    # return zipFile