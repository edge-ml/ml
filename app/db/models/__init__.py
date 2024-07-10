from bson.objectid import ObjectId
from app.DataModels.model import Model
from motor.motor_asyncio import AsyncIOMotorClient
from app.internal.config import DATABASE_URI, DATABASE_NAME
import asyncio
from pymongo import MongoClient

from app.db.db import get_db

class ModelDB():
    def __init__(self) -> None:
        mongo_client = MongoClient(DATABASE_URI)
        db = mongo_client[DATABASE_NAME]
        self._collection = db["models"]

    async def add_model(self, model: Model) -> ObjectId:
        res = await self._collection.insert_one(model.dict(by_alias=True))
        return res.inserted_id

    async def get_model(self, id: str, project_id: str) -> Model:
        query = {'_id': ObjectId(id), 'projectId': ObjectId(project_id)}
        res = await self._collection.find_one(query)
        return Model.parse_obj(res)

    def get_project_models(self, project_id: str):
        query = {'projectId': ObjectId(project_id)}
        res = self._collection.find(query)
        return [Model.parse_obj(model) for model in res]

    async def delete_model(self, id: ObjectId, projectId: ObjectId) -> None:
        query = {'_id': id, 'projectId': projectId}
        res = await self._collection.delete_one(query)
        return res.deleted_count > 0

    # async def update_model_status(id: str, project_id: str, status: ModelStatus):
    #     await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)}, {"$set": {"trainStatus": status.value}})

    # async def set_model_data(id: str, project_id: str, data):
    #     await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(project_id)}, {"$set": data})

    # async def set_train_error(id: ObjectId, projectId: ObjectId, errorMsg: str) -> None:
    #     await _models().update_one({'_id': ObjectId(id), 'projectId': ObjectId(projectId)}, {"$set": {"error": errorMsg}})

    async def update_model(self, project, model_id, model):
        model = Model(**model)
        query = {'_id': ObjectId(model_id), 'projectId': ObjectId(project)}
        operation = {"$set": model.model_dump(by_alias=True)}
        await self._collection.update_one(query, operation)