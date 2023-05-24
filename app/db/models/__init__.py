from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId
from app.DataModels.model import ModelStatus, Model

from app.db.db import get_db

def _models() -> AsyncIOMotorCollection:
    return get_db()['models']

async def add_model(model: Model) -> ObjectId:
    res = await _models().insert_one(model)
    return res.inserted_id

async def get_model(id: str, project_id: str) -> Model:
    obj = await _models().find_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)})
    if obj is None:
        raise RuntimeError("Model with given id doesn't exist")
    return Model.parse_obj(obj)

async def get_project_models(project_id: str):
    # TODO number of models that can be returned is limited by 10000
    objs = await _models().find({'projectId': ObjectId(project_id)}).to_list(length=10000)
    return objs

async def delete_model(id: str, project_id: ObjectId) -> None:
    await _models().delete_one({ '_id': ObjectId(id), 'projectId': ObjectId(project_id)})


async def update_model_status(id: str, project_id: str, status: ModelStatus):
    print(id, project_id, status.value)
    await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)}, {"$set": {"status": status.value}})

async def set_model_data(id: str, project_id: str, data):
    await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)}, {"$set": data})