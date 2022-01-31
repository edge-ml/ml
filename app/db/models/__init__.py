from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from app.db.db import get_db

from .model import Model

def _models() -> AsyncIOMotorCollection:
    return get_db()['models']

async def add_model(model: Model) -> ObjectId:
    res = await _models().insert_one(Model.marshal(model))
    return res.inserted_id


async def get_model(id: ObjectId) -> Model:
    obj = await _models().find_one({ '_id': id })
    if obj is None:
        raise RuntimeError("Model with given id doesn't exist")
    return Model.unmarshal(obj)
