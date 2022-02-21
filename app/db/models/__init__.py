from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from app.db.db import get_auth_db, get_db

from .model import Model
from .project import Project

def _models() -> AsyncIOMotorCollection:
    return get_db()['models']

def _projects() -> AsyncIOMotorCollection:
    return get_auth_db()['projects']

async def add_model(model: Model) -> ObjectId:
    res = await _models().insert_one(Model.marshal(model))
    return res.inserted_id

async def get_model(id: str) -> Model:
    obj = await _models().find_one({'_id': ObjectId(id)})
    if obj is None:
        raise RuntimeError("Model with given id doesn't exist")
    return Model.unmarshal(obj)

async def get_project_models(project_id: str) -> List[Model]:
    # TODO number of models that can be returned is limited by 10000
    objs = await _models().find({'project_id': project_id}).to_list(length=10000)
    objs =  [Model.unmarshal(obj) for obj in objs]
    return objs

async def delete_model(id: str) -> None:
    res = await _models().delete_one({ '_id': ObjectId(id)})
    print(res.deleted_count)

async def get_project(id: str) -> Project:
    obj = await _projects().find_one({'_id': ObjectId(id)})
    if obj is None:
        raise RuntimeError("Project with given id doesn't exist")
    return Project.unmarshal(obj)
