from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId
from DataModels.model import ModelStatus

from DataModels.db.model import MLModel


from db.db import get_db


def _models() -> AsyncIOMotorCollection:
    return get_db()['models']

async def add_model(model: MLModel) -> ObjectId:
    res = await _models().insert_one(model.dict(by_alias=True))
    return res.inserted_id

async def get_model(id: str, project_id: str) -> MLModel:
    query = {'_id': ObjectId(id), 'projectId': ObjectId(project_id)}
    obj = await _models().find_one(query)
    if obj is None:
        raise RuntimeError("Model with given id doesn't exist")
    return MLModel.model_validate(obj)

async def get_project_models(project_id: str) -> List[MLModel]:
    query = {'projectId': ObjectId(project_id)}
    objs = await _models().find(query).to_list(None)
    return [MLModel(**x) for x in objs]

async def delete_model(id: ObjectId, projectId: ObjectId) -> None:
    query = { '_id': ObjectId(id), 'projectId': ObjectId(projectId)}
    await _models().delete_one(query)

async def update_model_status(id: str, project_id: str, status: ModelStatus):
    query = {'_id': ObjectId(id), 'projectId': ObjectId(project_id)}
    update = {"$set": {"trainStatus": status.value}}
    await _models().update_one(query, update)

async def set_model_data(id: str, project_id: str, data):
    query = {'_id': ObjectId(id), 'projectId': ObjectId(project_id)}
    update = {"$set": data}
    await _models().update_one(query, update)

async def set_train_error(id: ObjectId, projectId: ObjectId, errorMsg: str) -> None:
    query = {'_id': ObjectId(id), 'projectId': ObjectId(projectId)}
    update = {"$set": {"error": errorMsg}}
    await _models().update_one(query, update)