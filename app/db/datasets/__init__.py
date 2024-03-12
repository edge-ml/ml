from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from db.db import get_datastore_db

from DataModels.labelings import LabelingModel

from DataModels.dataset import DatasetSchema

def _datasets() -> AsyncIOMotorCollection:
    return get_datastore_db()['datasets']

async def get_dataset(dataset_id: str, projectId: str) -> DatasetSchema:
    obj = await _datasets().find_one({'_id': ObjectId(dataset_id), 'projectId': ObjectId(projectId)})
    if obj is None:
        raise RuntimeError("Labeling with given id does not exist")
    return DatasetSchema.model_validate(obj=obj)