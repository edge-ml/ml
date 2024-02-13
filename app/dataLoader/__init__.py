from app.internal.config import TS_STORE_MECHANISM
from app.dataLoader.BaseDataLoader import BaseDataLoader
from app.dataLoader.FileSystemDataLoader import FileSystemDataLoader
from app.dataLoader.S3DataLoader import S3DataLoader

DATASTORE : BaseDataLoader = None
if TS_STORE_MECHANISM == "FS":
    DATASTORE = FileSystemDataLoader()
if TS_STORE_MECHANISM == "S3":
    DATASTORE = S3DataLoader()