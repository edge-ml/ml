from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from db.db import get_datastore_db

from DataModels.labelings import LabelingModel

from DataModels.model import Model

def _labelings() -> AsyncIOMotorCollection:
    return get_datastore_db()['labelings']

async def get_labeling(id: str, projectId: str) -> LabelingModel:
    obj = await _labelings().find_one({'_id': ObjectId(id), 'projectId': ObjectId(projectId)})
    if obj is None:
        raise RuntimeError("Labeling with given id does not exist")
    return LabelingModel.model_validate(obj=obj)