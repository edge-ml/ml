from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from app.db.db import get_auth_db

from .project import Project

def _projects() -> AsyncIOMotorCollection:
    return get_auth_db()['projects']

async def get_project(id: str) -> Project:
    obj = await _projects().find_one({'_id': ObjectId(id)})
    if obj is None:
        raise RuntimeError("Project with given id doesn't exist")
    return Project.unmarshal(obj)
