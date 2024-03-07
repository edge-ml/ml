from fastapi import APIRouter, Header, Response, BackgroundTasks
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.ml.Pipelines import PIPELINES_CONFIG
from app.DataModels import PipelineRequest
from app.ml.Pipelines import PIPELINEOPTIONCONFIGS

from app.DataModels.api import PipelineModel

from pydantic import BaseModel
from typing import List, Dict
from app.DataModels.parameter import Parameter

import json


router = APIRouter()


@router.get("/", response_model=List[PipelineModel])
async def get_pipelines():
    return [PipelineModel(**x) for x in PIPELINES_CONFIG]


# @router.get("/")
# async def get_pipelines():
#     return PIPELINES_CONFIG


@router.post("/")
async def train_a_model(body: PipelineRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    id = await train(body, project=project, background_tasks = background_tasks)
    return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")
    

@router.get("/pipeline/options")
async def get_pipeline_options(project: str = Header(...)):
    return PIPELINEOPTIONCONFIGS