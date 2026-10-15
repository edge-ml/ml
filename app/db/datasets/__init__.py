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

async def get_project_datasets_meta(projectId: str) -> List[dict]:
    """Ids, names, labelings and time-series names of every dataset in a
    project — without the time-series data."""
    cursor = _datasets().find(
        {'projectId': ObjectId(projectId)},
        {'name': 1, 'labelings.labelingId': 1, 'timeSeries._id': 1, 'timeSeries.name': 1},
    )
    return await cursor.to_list(length=None)
