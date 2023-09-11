from app.StorageProvider.BaseStorageProvider import BaseStorageProvider
from app.internal.config import CLASSIFIER_STORE
import numpy as np
from io import BytesIO
import os

class FileStorageProvider(BaseStorageProvider):
    def __init__(self):
        pass

    def save(self, id, data):
        path = f'{CLASSIFIER_STORE}/{str(id)}'
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        with open(path + "/clf.pkl", 'wb') as f:
            f.write(data)
    
    def load(cls, id):
        path = f'{CLASSIFIER_STORE}/{str(id)}'
        with open(path + "/clf.pkl", "rb") as f:
            return f.read()

    def delete(cls, id):
        path = f'{CLASSIFIER_STORE}/{str(id)}'
        try:
            os.rmdir(path)
        except FileNotFoundError:
            pass
        except OSError as e:
            print(f"An error occurred while trying to remove the directory '{path}': {e}")