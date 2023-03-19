from fastapi import APIRouter, Request, Header, Response, BackgroundTasks
from fastapi.param_functions import Depends
from app.routers.dependencies import validate_user
from app.models import EDGE_MODELS
from app.utils.PyObjectId import PyObjectId
from typing import List
from pydantic import BaseModel, Field
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.models import EDGE_MODELS


import traceback
import json
import orjson

router = APIRouter()


@router.get("/{model_id}/export/{format}")
async def export(format: str):
    pass
    # token = user_data[1]

    # timeseries = model.timeseries if model.timeseries else ["Sensor_A", "Sensor_B", "Sensor_C"]
    # labels = model.labels if model.labels else ["label1", "label2"]
    # wsize =  model.window_size if model.window_size else "<WINDOW_SIZE>"

    # form = InferenceFormats.from_str(format)
    # platform = next(x for x in platforms if form in x.supported_formats())

    # label_defs = fetch_label_definition(project_id, token)
    # label_names = [ (next(x for x in label_defs["labelTypes"] if x["_id"] == labelId))["name"] for labelId in labels ]

    # return platform.codegen(
    #     window_size = wsize,
    #     timeseries = timeseries,
    #     labels = label_names,
    #     format = form,
    #     scaler = model.scaler,
    #     windowing_mode = model.windowing_mode
    # )

@router.get("/{model_id}/download/{format}")
async def dlmodel(format: str):
    pass
    # print(model)
    # return Response(content=model.edge_model.export(InferenceFormats.from_str(format), model.window_size, model.labels, model.timeseries, model.scaler), media_type="text/plain")
