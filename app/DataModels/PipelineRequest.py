from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.utils.PyObjectId import PyObjectId
from bson.objectid import ObjectId
from app.DataModels.parameter import Parameter
from app.ml.Pipelines.Abstract.AbstractPipelineStep import StepType

class ConfigObj(BaseModel):
    name: str
    description: str
    parameters: List[Parameter]

class TrainDatasetModel(BaseModel):
    id : PyObjectId = Field(alias="_id")
    timeSeries: List[PyObjectId]
    class Config:
        json_encoders = {
            PyObjectId: str,
            ObjectId: str,
        }


class TrainLabelingModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    useZeroClass: bool
    disabledLabelIDs: List[PyObjectId]
    class Config:
        json_encoders = {
            PyObjectId: str,
            ObjectId: str,
        }
    
class PipelineStepOption(BaseModel):
    name: str
    description: str
    parameters: List[Parameter]
    state: Dict | None = None
    input_shape: List[int] | None = None
    output_shape: List[int] | None = None
    type: StepType | None = None
    metrics: Dict[str, Any] | None = None
    class Config:
        json_encoders = {
            PyObjectId: str,
            ObjectId: str,
        }

class PipelineStep(BaseModel):
    name: str
    description: str
    options: PipelineStepOption 
    type: StepType
    
    class Config:
        json_encoders = {
            PyObjectId: str,
            ObjectId: str,
        }

class SelectedPipeline(BaseModel):
    name: str
    description: str
    steps: List[PipelineStep]


class PipelineRequest(BaseModel):
    datasets: List[TrainDatasetModel]
    labeling: TrainLabelingModel
    selectedPipeline: SelectedPipeline
    name: str
    

