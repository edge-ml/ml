from fastapi import APIRouter, Request, Header, Response, BackgroundTasks
from fastapi.param_functions import Depends
from app.routers.dependencies import validate_user
from app.models import EDGE_MODELS
from app.utils.PyObjectId import PyObjectId
from typing import List, Dict
from pydantic import BaseModel, Field
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.models import EDGE_MODELS
from app.ml.Evaluation import getConfig
from app.DataModels.trainRequest import TrainRequest


import traceback
import json
import orjson

router = APIRouter()



@router.get("/")
async def models():
    data  = {
        "models": [x.config() for x in EDGE_MODELS],
        "evaluation": getConfig()
    }
    return data


@router.post("/")
async def models_train(body: TrainRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    id = await train(body, project=project, background_tasks = background_tasks)
    return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")