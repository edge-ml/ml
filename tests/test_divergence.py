import os
from tempfile import TemporaryDirectory
import unittest
import zipfile
import requests
from app.ml.Pipeline import Pipeline
from app.Deploy.Base import downloadModel
import numpy as np

from app.db.db import setup_db_connection
from app.db.models import get_model, _models
from app.ml.BaseConfig import Platforms

def run_prediction_py(csv_file_path, data_points_to_read, model):
    import csv
    pipeline = Pipeline.load(model.pipeline)

    data = np.genfromtxt(csv_file_path, delimiter=',', skip_header=0)
    # fake y label for window
    data = np.pad(data, ((0,0),(0,1)), mode='constant', constant_values=0)
    windowed, _ = pipeline.windower.window([data])
    windowed
    

class TestMLDivergenceCPPPython(unittest.IsolatedAsyncioTestCase):
    """Test if whether python and cpp inference diverges"""

    def setUp(self) -> None:
        setup_db_connection()

    async def test_devicemotion_data(self):
        """Test if cpp and python inference diverges with an example device motion dataset."""
        found_model = await _models().find_one({'name': 'test_devicemotion_model'})

        model_id = found_model['_id']
        project = found_model['projectId']

        model = await get_model(model_id, project)

        run_prediction_py('/home/omer/WorkRepos/ml/tests/testfornow/example_data.csv', 200, model)
        # code = downloadModel(model, Platforms.C)

        # with TemporaryDirectory() as tmpdir:
        #     zip_ref = zipfile.ZipFile(code)
        #     zip_ref.extractall(tmpdir)
        #     print('')