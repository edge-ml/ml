from pydantic import BaseModel
from app.DataModels.parameter import Parameter
from typing import List, Dict, Optional

class PipeLineStep(BaseModel):
    name: str
    parameters: Optional[List[Parameter]]
    state: Optional[Dict]

class PipelineModel(BaseModel):
    windower: PipeLineStep
    featureExtractor: PipeLineStep
    normalizer: PipeLineStep
    classifier: PipeLineStep
    labels : List[str]
    timeSeries: List[str]
    samplingRate: float

