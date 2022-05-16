from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.internal.config import AUTH_DATABASE_NAME, DATABASE_URI, DATABASE_NAME
import asyncio

_db = None
_auth_db = None

def setup_db_connection():
    global _db
    global _auth_db
    _client = AsyncIOMotorClient(DATABASE_URI)
    _client.get_io_loop = asyncio.get_running_loop
    _db = _client[DATABASE_NAME]
    _auth_db = _client[AUTH_DATABASE_NAME]

def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database is not connected")
    return _db

def get_auth_db() -> AsyncIOMotorDatabase:
    if _auth_db is None:
        raise RuntimeError("Auth database is not connected")
    return _auth_db