from app.ml.Pipelines.Categories.Normalizer import get_normalizer_by_name
from app.DataModels.model import Model
from app.ml.BaseConfig import Platforms
from app.ml.Pipelines import getPipeline
from io import BytesIO
from app.utils.zipfile import zipFiles
from app.utils.StringFile import StringFile
import zipfile
import io

# def downloadModel(model, platform: Platforms):
#     pipeline = getPipeline(model)
#     files = pipeline.export(model, platform)

#     zip_buffer = io.BytesIO()
#     print(files)
#     with zipfile.ZipFile(zip_buffer, 'w') as zipf:
#         # Add each string as a separate file in the zip archive
#         for i, file in enumerate(files):
#             zipf.writestr(file.name, file.content)
#     zip_buffer.seek(0)
#     return zip_buffer.read()

def downloadModel(model, platform: Platforms):
    pipeline = getPipeline(model)
    files = pipeline.export(model, platform)
    files = [StringFile(file.content, file.name) for file in files]
    return zipFiles(files)

