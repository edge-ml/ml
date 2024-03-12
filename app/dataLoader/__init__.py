from internal.config import TS_STORE_MECHANISM
from dataLoader.BaseDataLoader import BaseDataLoader
from dataLoader.FileSystemDataLoader import FileSystemDataLoader
from dataLoader.S3DataLoader import S3DataLoader

DATASTORE : BaseDataLoader = None
if TS_STORE_MECHANISM == "FS":
    DATASTORE = FileSystemDataLoader()
if TS_STORE_MECHANISM == "S3":
    DATASTORE = S3DataLoader()