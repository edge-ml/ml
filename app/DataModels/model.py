from app.utils.PyObjectId import PyObjectId
from bson.objectid import ObjectId
from typing import List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class ModelStatus(str, Enum):
    waiting = "waiting"
    preprocessing = "preprocessing"
    fitting_model = "fitting model"
    done = "done"


class Hyperparameter(BaseModel):
    name: str
    value: str

class TrainingDataset(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class Model(BaseModel):
    id : PyObjectId = Field(default_factory=ObjectId, alias="_id")
    projectId: PyObjectId = Field(default_factory=ObjectId)
    name: str
    trainRequest: Dict
    status: ModelStatus = ModelStatus.waiting