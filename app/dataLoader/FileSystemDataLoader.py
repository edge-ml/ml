from app.dataLoader.BaseDataLoader import BaseDataLoader
import struct
import numpy as np
import os
from app.internal.config import TSDATA

DATA_PREFIX = TSDATA

class FileSystemDataLoader(BaseDataLoader):

    def __init__(self):
        if not os.path.exists(DATA_PREFIX):
            os.makedirs(DATA_PREFIX)


    def load_series(self, id):
        path = os.path.join(DATA_PREFIX, id + ".bin")
        print(path)
        with open(path, "rb") as f:
            data_len = struct.unpack("I", f.read(4))[0]
            time_arr = np.asarray(struct.unpack("Q" * data_len, f.read(data_len * 8)), dtype=np.uint64)
            data_arr = np.asarray(struct.unpack("f" * data_len, f.read(data_len * 4)), dtype=np.float32)
            return time_arr, data_arr

    def save_series(self, id, time_arr, data_arr):
        with open(os.path.join(DATA_PREFIX, id + ".bin"), "wb") as f:
            f.write(struct.pack("I", len(time_arr)))
            f.write(struct.pack("Q" * len(time_arr), *time_arr))
            f.write(struct.pack("f" * len(data_arr), *data_arr))

    def delete(self, id):
        path = os.path.join(DATA_PREFIX, id + ".bin")
        os.remove(path)