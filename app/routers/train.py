from fastapi import APIRouter, Header, Response, BackgroundTasks, Request
from utils.jsonEncoder import JSONEncoder
from ml.trainer import train
from ml.Pipelines import PIPELINES_CONFIG
from DataModels import PipelineRequest
from ml.Pipelines import PIPELINEOPTIONCONFIGS
from typing import Dict
from controller.trainController import register_train

from DataModels.api import PipelineModel

from typing import List

import json


router = APIRouter()


@router.get("/", response_model=List[PipelineModel])
async def get_pipelines():
    return PIPELINES_CONFIG



@router.post("/")
async def train_a_model(body: PipelineRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    register_train(project, body)
    return None
    
    # id = await train(body, project=project, background_tasks = background_tasks)
    # return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")
    

@router.get("/pipeline/options")
async def get_pipeline_options(project: str = Header(...)):
    return PIPELINEOPTIONCONFIGS