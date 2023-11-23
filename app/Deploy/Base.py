from app.ml.Normalizer import get_normalizer_by_name
from app.DataModels.model import Model
from app.ml.BaseConfig import Platforms
from app.ml.Pipeline import Pipeline
from app.Deploy.Devices.BaseDevice import QuantizationLevels
from io import BytesIO
import zipfile

def downloadModel(model, platform: Platforms, quantization_level: QuantizationLevels):
    pipeline = Pipeline.load(model.pipeline)
    zipFile = pipeline.generateModelData(platform, quantization_level)
    return zipFile