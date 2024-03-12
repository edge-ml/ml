# Consts
import os
from os.path import join
import struct
import numpy as np
from scipy.signal import resample
import lttbc
import h5py
import functools
import tempfile
from internal.config import TS_STORE_MECHANISM
from dataLoader.FileSystemDataLoader import FileSystemDataLoader
from dataLoader.S3DataLoader import S3DataLoader

dataLoader = None

# Set the correct dataloader
if TS_STORE_MECHANISM == "FS":
    dataLoader = FileSystemDataLoader()
if TS_STORE_MECHANISM == "S3":
    dataLoader = S3DataLoader()


class BinaryStore():

    def __init__(self, _id) -> None:
        self._id = str(_id)
        self.time_arr = np.array([], dtype=np.uint64)
        self.data_arr = np.array([], dtype=np.float32)
    
    def loadSeries(self):
        self.time_arr, self.data_arr = dataLoader.load_series(self._id)

    def getHdf5Stream(self):
        self.loadSeries()
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            with h5py.File(tmp_file.name, "w") as hf:
                hf.create_dataset("time", data=self.time_arr)
                hf.create_dataset("data", data=self.data_arr)
                print(self.data_arr)
            return tmp_file.name

    def saveSeries(self):
        dataLoader.save_series(self._id, self.time_arr, self.data_arr)
        

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
        time_diff = np.diff(self.time_arr)
        sampling_rate_mean = np.nan_to_num(np.mean(time_diff)) if len(time_diff) > 0 else -1
        sampling_rate_var = np.nan_to_num(np.var(time_diff)) if len(time_diff) > 0 else -1
        if len(self.time_arr) == 0:
            return None, None, {"mean": 0, "var": 0}, 0
        return int(self.time_arr[0]), int(self.time_arr[-1]), {"mean": sampling_rate_mean, "var": sampling_rate_var}, len(self.time_arr) # start, end


    def delete(self):
        dataLoader.delete(self._id)