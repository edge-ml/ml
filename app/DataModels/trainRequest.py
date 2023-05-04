from typing import Dict, List
from pydantic import BaseModel, Field
from app.utils.PyObjectId import PyObjectId
from app.DataModels.parameter import Parameter

class ConfigObj(BaseModel):
    name: str
    description: str
    parameters: List[Parameter]

class TrainDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class TrainLabelingModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    useZeroClass: bool

class TrainRequest(BaseModel):
    name: str
    useBestModelFromEvaluation: bool = False
    datasets: List[TrainDatasetModel]
    labeling: TrainLabelingModel
    classifier: ConfigObj
    evaluation: ConfigObj
    windowing: ConfigObj
    normalizer: ConfigObj
    featureExtractor: ConfigObj