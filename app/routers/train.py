from fastapi import APIRouter, Header, Response, BackgroundTasks
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.ml.Pipelines.ManualClassificationPipeline import ManualClassificationPipeline 
from app.DataModels.trainRequest import TrainRequest
from app.ml.Pipelines.Categories.Normalizer import NORMALIZER_CONFIG
from app.ml.Pipelines.Categories.Classifier import CLASSIFIER_CONFIG
from app.ml.Pipelines.Categories.Evaluation import EVALUATION_CONFIG
from app.ml.Pipelines.Categories.Windowing import WIDNOWING_CONFIG
from app.ml.Pipelines.Categories.FeatureExtraction import FEATURES_CONFIG
from app.ml.Pipelines import PIPELINES_CONFIG
from app.DataModels import PipelineRequest

import json


from app.ml.Pipelines import get_configs

router = APIRouter()


@router.post("/")
async def models_train(body: PipelineRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    id = await train(body, project=project, background_tasks = background_tasks)
    return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")
    


@router.get("/")
async def get_pipelines():
    return PIPELINES_CONFIG