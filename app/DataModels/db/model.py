from pydantic import BaseModel, Field
from typing import Optional, List
from utils.PyObjectId import PyObjectId


class PipelineDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]

class PipelineLabelingModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    useZeroClass: bool
    disabledLabelIDs = List[PyObjectId]


class PipelineModel(BaseModel):
    datasets: List[PipelineDatasetModel]
    labeling: PipelineLabelingModel


class MLModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    projectId: PyObjectId
    name: str
    pipeline: PipelineModel
    samplingRate: Optional[float] = None
