from app.db.models import get_model
from app.ml.Pipelines import getPipeline
from app.dataLoader import DATASTORE

from app.codegen.inference.InferenceFormats import InferenceFormats

from fastapi.responses import Response
import zipfile
from io import BytesIO

def as_download(data, zip_name):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", False) as zip_file:
        for file_data in data:
            fileName = file_data["name"]
            fileContent = file_data["buffer"]
            zip_file.writestr(fileName, fileContent.getvalue())
    zip_buffer.seek(0)
    return Response(content=zip_buffer.getvalue(), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={zip_name}.zip"})

async def download_model(model_id, project_id, language):
    model = await get_model(model_id, project_id)
    model_name = model.name
    if language == "python":
        data = []
        pipeline = getPipeline(model)
        for option in pipeline.options:
            if InferenceFormats.PYTHON in option.get_platforms():
                raw = option.as_file()
                data.append(raw)
        return as_download(data, model_name)


