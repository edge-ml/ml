from app.utils.PyObjectId import PyObjectId
from bson.objectid import ObjectId
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from app.DataModels.trainRequest import TrainRequest
from app.DataModels.parameter import Parameter
from app.DataModels.PipeLine import PipelineModel
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


# class Model(BaseModel):
#     id : PyObjectId = Field(default_factory=ObjectId, alias="_id")
#     projectId: PyObjectId = Field(default_factory=ObjectId)
#     name: str
#     trainRequest: TrainRequest
#     pipeline: Optional[PipelineModel]
#     timeSeries: Optional[List[str]]
#     status: ModelStatus = ModelStatus.waiting
#     error: str = Field(default="")

class Model(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    projectId: PyObjectId
    name: str
    pipeLineRequest: PipelineRequest
    timeSeries: Optional[List[str]]
    trainStatus: ModelStatus = ModelStatus.waiting
    errorText: str = Field(default="")


