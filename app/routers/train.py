from fastapi import APIRouter, Header, Response, BackgroundTasks
from app.utils.jsonEncoder import JSONEncoder
from app.ml.trainer import train
from app.ml.Evaluation import getConfig
from app.DataModels.trainRequest import TrainRequest
from app.ml.Normalizer import NORMALIZER_CONFIG
from app.ml.Classifier import CLASSIFIER_CONFIG
from app.ml.Evaluation import EVALUATION_CONFIG
from app.ml.Windowing import WIDNOWING_CONFIG
from app.ml.FeatureExtraction import FEATURES_CONFIG
import json

router = APIRouter()



@router.get("/")
async def models():
    data  = {
        "classifier": CLASSIFIER_CONFIG,
        "normalizer": NORMALIZER_CONFIG,
        "evaluation": EVALUATION_CONFIG,
        "windowing": WIDNOWING_CONFIG,
        "featureExtractors": FEATURES_CONFIG
    }
    return data


@router.post("/")
async def models_train(body: TrainRequest, background_tasks: BackgroundTasks, project: str = Header(...)):
    id = await train(body, project=project, background_tasks = background_tasks)
    return Response(json.dumps(id, cls=JSONEncoder), media_type="application/json")