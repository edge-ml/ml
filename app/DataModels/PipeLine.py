from pydantic import BaseModel
from app.DataModels.parameter import Parameter
from typing import List, Dict

class PipeLineStep(BaseModel):
    name: str
    parameters: List[Parameter]
    state: Dict

class PipelineModel(BaseModel):
    windower: PipeLineStep
    featureExtractor: PipeLineStep
    normalizer: PipeLineStep
    classifier: PipeLineStep
    labels : List[str]
    timeSeries: List[str]

