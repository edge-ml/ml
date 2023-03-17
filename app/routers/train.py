from fastapi import APIRouter, Request, Header, Response, BackgroundTasks
from fastapi.param_functions import Depends
from app.routers.dependencies import validate_user
from app.models import EDGE_MODELS
from app.utils.PyObjectId import PyObjectId
from typing import List
from pydantic import BaseModel, Field
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train

import traceback
import json
import orjson

router = APIRouter()


class ModelInfo(BaseModel):
    hyperparameters: List
    classifier: str

class TrainDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class TrainRequest(BaseModel):
    name: str
    datasets: List[TrainDatasetModel]
    labeling: PyObjectId
    name: str
    modelInfo: ModelInfo


@router.post("/")
async def models_train(body: TrainRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    id = await train(body, project=project, background_tasks = background_tasks)
    return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")