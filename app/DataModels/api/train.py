from pydantic import BaseModel
from typing import List

from app.DataModels.common import Parameter


class PipelineStepOption(BaseModel):
    name: str
    description: str
    parameters: List[Parameter]


class PipelineStep(BaseModel):
    name: str
    description: str
    type: str
    options: List[PipelineStepOption]


class PipelineModel(BaseModel):
    name: str
    description: str
    steps: List[PipelineStep]
