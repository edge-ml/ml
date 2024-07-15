from app.utils.PyObjectId import PyObjectId
from bson.objectid import ObjectId
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum
from app.DataModels.parameter import Parameter
from app.DataModels.PipelineRequest import PipelineRequest


class ModelStatus(str, Enum):
    waiting = "waiting"
    training = "training"
    done = "done"
    error = "error"


class Hyperparameter(BaseModel):
    name: str
    value: str

class TrainingDataset(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class ConfigObj(BaseModel):
    name: str
    parameters: List[Parameter]
    state: Optional[Dict]

class TrainDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class TrainLabelingModel(BaseModel):
    _id: PyObjectId
    useZeroClass: bool

class TrainRequest(BaseModel):
    name: str
    useBestModelFromEvaluation: bool = False
    datasets: List[TrainDatasetModel]
    labeling: TrainLabelingModel
    name: str
    classifier: ConfigObj
    evaluation: ConfigObj
    windowing: ConfigObj
    normalizer: ConfigObj
    featureExtractor: ConfigObj


class ModelStoreObj(BaseModel):
    name: str
    parameters: List[Parameter]
    state: Optional[Dict]

class ModelConfig(BaseModel):
    classifier: ModelStoreObj
    evaluation: ModelStoreObj
    windower: ModelStoreObj
    normalizer: ModelStoreObj
    featureExtractor: ModelStoreObj

class ConcreteStepDefinitions(BaseModel):
    name: str
    description: str
    type: str

class ConcreteSteps(BaseModel):
    options: List[ConfigObj]
    # steps: List[ConcreteStepDefinitions]

class Labeling(BaseModel):
    name: str
    color: str


class Model(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    projectId: PyObjectId
    name: str
    pipeline: PipelineRequest 
    labels: List[Labeling] | None = None
    timeSeries: List[str] | None = None
    samplingRate: float | None = None
    trainStatus: ModelStatus = ModelStatus.waiting
    error: str = Field(default="")

    class Config:
        json_encoders = {
            PyObjectId: str,
            ObjectId: str
        }


