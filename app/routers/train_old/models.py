from fastapi import APIRouter, Request, Header, Response, BackgroundTasks
from fastapi.param_functions import Depends
from routers.dependencies import validate_user
from models import EDGE_MODELS
from utils.PyObjectId import PyObjectId
from typing import List
from pydantic import BaseModel
from utils.jsonEncoder import JSONEncoder


# import traceback
# import json
# import orjson

# router = APIRouter()

# class Training(BaseModel):
#     id: str
#     name: str
#     training_state: TrainingState
#     error_msg: str

# class ModelInfo(BaseModel):
#     hyperparameters: List
#     classifier: str

# class TrainDatasetModel(BaseModel):
#     id : PyObjectId = Field(alias="_id")
#     timeSeries: List[PyObjectId]

# class TrainRequest(BaseModel):
#     name: str
#     datasets: List[TrainDatasetModel]
#     labeling: PyObjectId
#     name: str
#     modelInfo: ModelInfo


# @router.get("/{model_id}")
# async def getModels(model_id, project: str = Header(...), user_data=Depends(validate_user)):
    
