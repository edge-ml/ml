from pydantic import BaseModel
from bson.objectid import ObjectId
from app.utils.PyObjectId import PyObjectId
from pydantic import Field
from typing import Optional, List, Dict

class TimeSeries(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    start: int
    end: int
    unit: str = Field(default="")
    name: str
    data: Optional[List]

class DatasetLabels(BaseModel):
    start: int
    end: int
    type: PyObjectId
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")

class DatasetLabeling(BaseModel):
    labelingId: PyObjectId
    labels: List[DatasetLabels]

class DatasetSchema(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    projectId: PyObjectId = Field(default_factory=ObjectId)
    name: str
    start: int
    end: int
    metaData: Dict[str, str] = Field(default={})
    timeSeries: List[TimeSeries]
    labelings: List[DatasetLabeling] = Field(default=[])