from typing import List
from fastapi import APIRouter, Depends, Response
from app.codegen.inference.InferenceFormats import InferenceFormats

from app.db.models import get_model
from app.db.models.model import Model
from app.routers.dependencies import validate_model
from app.codegen.inference import platforms

router = APIRouter()

@router.get("/{model_id}/export/{format}")
async def export(format: str, model: Model = Depends(validate_model)):
    timeseries = model.timeseries if model.timeseries else ["Sensor_A", "Sensor_B", "Sensor_C"]
    labels = model.labels if model.labels else []
    wsize =  model.window_size if model.window_size else "<WINDOW_SIZE>"

    form = InferenceFormats.from_str(format)
    platform = next(x for x in platforms if form in x.supported_formats())

    return platform.codegen(
        window_size = wsize,
        timeseries = timeseries,
        labels = labels,
        format = form
    )

@router.get("/{model_id}/download/{format}")
async def dlmodel(format: str, model=Depends(validate_model)):
    return Response(content=model.edge_model.export(InferenceFormats.from_str(format), model.window_size, model.labels, model.timeseries), media_type="text/plain")
