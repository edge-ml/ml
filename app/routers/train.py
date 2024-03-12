from fastapi import APIRouter, Header, Response, BackgroundTasks
from utils.jsonEncoder import JSONEncoder
from ml.trainer import train
from ml.Pipelines import PIPELINES_CONFIG
from DataModels import PipelineRequest
from ml.Pipelines import PIPELINEOPTIONCONFIGS
from DataModels.parameter import Parameter, NumberParameter, SelectionParameter, TextParameter

from DataModels.api import PipelineModel

from pydantic import BaseModel
from typing import List, Dict
from DataModels.parameter import Parameter
from DataModels.api.train import PipelineStepOption

import json


router = APIRouter()


# @router.get("/", response_model=List[PipelineModel])
@router.get("/")
async def get_pipelines():

    for step in PIPELINES_CONFIG[0]["steps"]:
        for option in step["options"]:
            for parameter in option["parameters"]:
                # Parameter.model_validate(parameter)
                print(type(parameter))
                print("+"*40)
            PipelineStepOption.model_validate(option)
            return
    # parameter = PIPELINES_CONFIG[0]["steps"][0]["options"][0]["parameters"][0]
    # number_param = NumberParameter.model_validate(parameter)
    return None
    # return [PipelineModel.model_validate(x) for x in PIPELINES_CONFIG]


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