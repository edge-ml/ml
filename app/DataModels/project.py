from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from app.utils.PyObjectId import PyObjectId
from typing import List

class Project(BaseModel):
    id: PyObjectId =  Field(alias="_id")
    admin: PyObjectId =  Field()
    name: str
    enableDeviceApi: bool
    user: List[PyObjectId] = Field(default=[])

