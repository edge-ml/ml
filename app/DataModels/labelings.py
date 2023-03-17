from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from app.utils.PyObjectId import PyObjectId
from typing import List

class LabelModel(BaseModel):
    name: str
    color: str
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")

class LabelingModel(BaseModel):
    name: str
    labels: List[LabelModel]
    projectId: PyObjectId
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")


