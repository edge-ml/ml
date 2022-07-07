from typing import List
from fastapi import APIRouter, Depends, Response
from app.codegen.inference.InferenceFormats import InferenceFormats

from app.db.models import get_model
from app.db.models.model import Model
from app.internal.data_collection import fetch_label_definition
from app.routers.dependencies import extract_project_id, validate_model, validate_user
from app.codegen.inference import platforms

router = APIRouter()

@router.get("/{model_id}/export/{format}")
async def export(format: str, model: Model = Depends(validate_model), user_data=Depends(validate_user), project_id=Depends(extract_project_id)):
    token = user_data[1]

    timeseries = model.timeseries if model.timeseries else ["Sensor_A", "Sensor_B", "Sensor_C"]
    labels = model.labels if model.labels else []
    wsize =  model.window_size if model.window_size else "<WINDOW_SIZE>"

    form = InferenceFormats.from_str(format)
    platform = next(x for x in platforms if form in x.supported_formats())

    label_defs = fetch_label_definition(project_id, token)
    label_names = [ (next(x for x in label_defs["labelTypes"] if x["_id"] == labelId))["name"] for labelId in labels ]

    return platform.codegen(
        window_size = wsize,
        timeseries = timeseries,
        labels = label_names,
        format = form,
    )

@router.get("/{model_id}/download/{format}")
async def dlmodel(format: str, model=Depends(validate_model)):
    print(model)
    return Response(content=model.edge_model.export(InferenceFormats.from_str(format), model.window_size, model.labels, model.timeseries, model.scaler), media_type="text/plain")
