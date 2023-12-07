from fastapi import APIRouter, Header, Response, BackgroundTasks
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.ml.Pipelines import PIPELINES_CONFIG
from app.DataModels import PipelineRequest
from app.ml.Pipelines import PIPELINEOPTIONCONFIGS

import json



router = APIRouter()


@router.post("/")
async def models_train(body: PipelineRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    id = await train(body, project=project, background_tasks = background_tasks)
    return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")
    

@router.get("/")
async def get_pipelines():
    return PIPELINES_CONFIG

@router.get("/pipeline/options")
async def get_pipeline_options(project: str = Header(...)):
    return PIPELINEOPTIONCONFIGS