from typing import Dict, List
from pydantic import BaseModel, Field
from app.utils.PyObjectId import PyObjectId

class Classififer(BaseModel):
    name: str
    description: str
    parameters: List

class TrainDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class Normalizer(BaseModel):
    name: str
    parameters: Dict

class Windower(BaseModel):
    name: str
    description: str
    parameters: List[Dict]

class Features(BaseModel):
    name: str
    parameters: List[Dict]

class TrainRequest(BaseModel):
    name: str
    datasets: List[TrainDatasetModel]
    labeling: PyObjectId
    name: str
    classifier: Classififer
    evaluation: Dict
    windowing: Windower
    normalizer: Normalizer
    featureExtractor: Features