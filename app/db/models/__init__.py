from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from app.db.db import get_db
from app.db.deployments import delete_all_deployments_of_model

from .model import Model

def _models() -> AsyncIOMotorCollection:
    return get_db()['models']

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
    await delete_all_deployments_of_model(id) # mongo not relational
    await _models().delete_one({ '_id': ObjectId(id)})
