from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId
from app.DataModels.model import ModelStatus, Model
from app.utils.PyObjectId import PyObjectId

from app.db.db import get_db


from pydantic import BaseModel, Field



class PipelineDbStepOption(BaseModel):
    name: str
    desciption: str
    parameters: List[ParameterDBModel]
    state: Dict
    input_shape: Optional[List]
    output_shape: Optional[List]

class PipelineDbStepModel(BaseModel):
    name: str
    desciption: str
    options: List[PipelineDbStepOption]
    type: str


class SelectedPipelineDbModel(BaseModel):
    name: str
    description: str
    steps: List[]

class PipelineDbModel(BaseModel):
    datasets: List[PyObjectId]
    labeling: List[PyObjectId]
    selectedPipeline: SelectedPipelineDbModel
    name: str

class MLModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    projectId: PyObjectId
    name: str
    pipeline: PipelineDbModel
    timeSeries: List[str]
    samplingRate: float
    trainStatus: str
    error: str



def _models() -> AsyncIOMotorCollection:
    return get_db()['models']

async def add_model(model: Model) -> ObjectId:
    res = await _models().insert_one(model.dict(by_alias=True))
    return res.inserted_id

async def get_model(id: str, project_id: str) -> Model:
    obj = await _models().find_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)})
    if obj is None:
        raise RuntimeError("Model with given id doesn't exist")
    return Model.parse_obj(obj)

async def get_project_models(project_id: str):
    objs = await _models().find({'projectId': ObjectId(project_id)})
    return objs

async def delete_model(id: ObjectId, projectId: ObjectId) -> None:
    print("Delete", id, projectId)
    await _models().delete_one({ '_id': ObjectId(id), 'projectId': ObjectId(projectId)})

async def update_model_status(id: str, project_id: str, status: ModelStatus):
    print(id, project_id, status.value)
    await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)}, {"$set": {"trainStatus": status.value}})

async def set_model_data(id: str, project_id: str, data):
    await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)}, {"$set": data})

async def set_train_error(id: ObjectId, projectId: ObjectId, errorMsg: str) -> None:
    await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(projectId)}, {"$set": {"error": errorMsg}})