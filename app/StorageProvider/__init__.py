from app.internal.config import TS_STORE_MECHANISM
from app.StorageProvider.S3StorageProvider import S3StorageProvider
from app.StorageProvider.BaseStorageProvider import BaseStorageProvider

StorageProvider : BaseStorageProvider = None
if TS_STORE_MECHANISM == "S3":
    StorageProvider = S3StorageProvider()
