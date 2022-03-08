from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from uuid import UUID

from .deployment import Deployment

from app.db.db import get_db

def _deployments() -> AsyncIOMotorCollection:
    return get_db()['deployments']

async def add_deployment(deployment: Deployment) -> str:
    res = await _deployments().insert_one(Deployment.marshal(deployment))
    return str(res.inserted_id)

async def get_deployment(key: str) -> Deployment:
    obj = await _deployments().find_one({'_id': UUID(key)})
    if obj is None:
        raise RuntimeError("Deployment with given key doesn't exist")
    return Deployment.unmarshal(obj)

async def get_model_deployments(project_id: str, model_id: str) -> List[Deployment]:
    # TODO number of deployments that can be returned is limited by 10000
    objs = await _deployments().find({'project_id': project_id, 'model_id': model_id}).to_list(length=10000)
    objs =  [Deployment.unmarshal(obj) for obj in objs]
    return objs

async def delete_deployment(key: str) -> None:
    res = await _deployments().delete_one({ '_id': UUID(key) })
    return res.deleted_count

async def delete_all_deployments_of_model(model_id: str) -> None:
    res = await _deployments().delete_many({ 'model_id': model_id })
    return res.deleted_count

async def rename_deployment(key: str, name: str) -> None:
    res = await _deployments().update_one({'_id': UUID(key)}, {'$set': {'name': name}})
    return res.modified_count

