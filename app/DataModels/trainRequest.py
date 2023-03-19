from typing import Dict, List
from pydantic import BaseModel, Field
from app.utils.PyObjectId import PyObjectId

class ModelInfo(BaseModel):
    hyperparameters: List
    classifier: str

class TrainDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class Normalizer(BaseModel):
    name: str
    parameters: Dict

class TrainRequest(BaseModel):
    name: str
    datasets: List[TrainDatasetModel]
    labeling: PyObjectId
    name: str
    modelInfo: ModelInfo
    evaluation: Dict
    normalizer: Normalizer