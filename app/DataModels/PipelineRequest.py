from typing import Dict, List
from pydantic import BaseModel, Field
from app.utils.PyObjectId import PyObjectId
from app.DataModels.parameter import Parameter
from app.ml.Pipelines.Abstract.AbstractPipelineStep import StepType

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
    disabledLabelIDs: List[PyObjectId]
    
class PipelineStepOption(BaseModel):
    name: str
    description: str
    parameters: List[Parameter]

class PipelineStep(BaseModel):
    name: str
    description: str
    options: PipelineStepOption 
    type: StepType


class SelectedPipeline(BaseModel):
    name: str
    description: str
    steps: List[PipelineStep]


class PipelineRequest(BaseModel):
    datasets: List[TrainDatasetModel]
    labeling: TrainLabelingModel
    selectedPipeline: SelectedPipeline
    name: str
    

