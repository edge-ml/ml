from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from app.db.db import get_datastore_db

from app.DataModels.labelings import LabelingModel

from app.DataModels.dataset import DatasetSchema

def _datasets() -> AsyncIOMotorCollection:
    return get_datastore_db()['datasets']

async def get_dataset(dataset_id: str, projectId: str) -> DatasetSchema:
    obj = await _datasets().find_one({'_id': ObjectId(dataset_id), 'projectId': ObjectId(projectId)})
    if obj is None:
        raise RuntimeError("Labeling with given id does not exist")
    return DatasetSchema.parse_obj(obj=obj)