from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.internal.config import DATABASE_URI, DATABASE_NAME

_db = None

def setup_db_connection():
    global _db
    _client = AsyncIOMotorClient(DATABASE_URI)
    _db = _client[DATABASE_NAME]


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database is not connected")
    return _db