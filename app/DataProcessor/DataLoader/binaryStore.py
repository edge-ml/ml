# Consts
import os
from os.path import join
import struct
import numpy as np
from scipy.signal import resample
# import lttbc
import functools


DATA_PREFIX = "../TS_DATA"


# @functools.lru_cache(maxsize=512)
def _readSeries(path):
    with open(path, "rb") as f:
        len = struct.unpack("I", f.read(4))[0]
        time_arr = np.asarray(struct.unpack("Q" * len, f.read(len * 8)), dtype=np.uint64)
        data_arr = np.asarray(struct.unpack("f" * len, f.read(len * 4)), dtype=np.float32)
        return time_arr, data_arr


class BinaryStore():

    def __init__(self, _id) -> None:
        self._id = str(_id)
        self.time_arr = np.array([], dtype=np.uint64)
        self.data_arr = np.array([], dtype=np.float32)

        if not os.path.exists(DATA_PREFIX):
            os.makedirs(DATA_PREFIX)

        self._path = join(DATA_PREFIX, self._id + ".bin")
    
    def loadSeries(self):
        self.time_arr, self.data_arr = _readSeries(self._path)

    def saveSeries(self):
        with open(join(DATA_PREFIX, self._id + ".bin"), "wb") as f:
            f.write(struct.pack("I", len(self.time_arr)))
            f.write(struct.pack("Q" * len(self.time_arr), *self.time_arr))
            f.write(struct.pack("f" * len(self.data_arr), *self.data_arr))

    def getPart(self, start_time, end_time, max_resolution=None):
        max_resolution = int(float(max_resolution))

        if len(self.time_arr) < 200:
            res = np.asarray([self.time_arr, self.data_arr]).T
            res = np.ascontiguousarray(res)
            return res


        start_index = 0
        end_index = len(self.time_arr) -1
        if start_time != "undefined" and end_time != "undefined":
            end_time = int(end_time)
            start_time = int(start_time)
            [start_index, end_index] = np.searchsorted(self.time_arr, [start_time, end_time])
        time_res = self.time_arr[start_index:end_index]
        data_res = self.data_arr[start_index:end_index]

        if max_resolution is not None and len(time_res) > max_resolution:
            [time_res, data_res] = lttbc.downsample(time_res, data_res, max_resolution)
        res = np.asarray([time_res, data_res]).T
        res = np.ascontiguousarray(res)
        return res



    def getFull(self):
        return {"time": self.time_arr, "data": self.data_arr}

    def append(self, tsValues):
        if len(tsValues) == 0:
            time, data = np.array([], dtype=np.uint64), np.array([], dtype=np.float32)
        else:
            time, data = list(zip(*tsValues))
            time, data = list(time), list(data)
        return self._appendValues(time, data)

    def _appendValues(self, time, data):
        time = np.array(time, dtype=np.uint64)
        data = np.array(data, dtype=np.float32)
        oldLen = len(self.time_arr)
        self.time_arr = np.append(self.time_arr, time)
        self.data_arr = np.append(self.data_arr, data)
        assert(oldLen + len(time) == len(self.time_arr))
        inds = self.time_arr.argsort()
        self.time_arr = self.time_arr[inds]
        self.data_arr = self.data_arr[inds]
        self.saveSeries()
        if len(self.time_arr) == 0:
            return None, None
        return int(self.time_arr[0]), int(self.time_arr[-1]) # Return start and end


    def delete(self):
        os.remove(self._path)