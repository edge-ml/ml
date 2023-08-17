import json
import os
from tempfile import TemporaryDirectory
import unittest
import zipfile
import numpy as np
from jinja2 import Template, Markup
import subprocess
import shutil
import asyncio

from app.Deploy.Base import downloadModel
from app.db.db import setup_db_connection
from app.db.models import get_model, _models
from app.ml.BaseConfig import Platforms
from app.ml.Pipeline import Pipeline

fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

def run_prediction_pipeline(csv_file_path, data_points_to_read, model):
    pipeline = Pipeline.load(model.pipeline)

    data = np.genfromtxt(csv_file_path, delimiter=',', skip_header=0, max_rows=data_points_to_read)
    data = np.pad(data, ((0,0),(1,0)), mode='constant', constant_values=0) # add a zero column for the timestamp, as feature extraction expects it (and removes it)

    assert pipeline.windower.get_name() == 'Sample based'
    window_size = int(pipeline.windower.get_param_value_by_name('window_size'))
    windowed = np.lib.stride_tricks.sliding_window_view(data, window_shape=(window_size, data.shape[-1])).squeeze(1)

    features, _ = pipeline.featureExtractor.extract_features(windowed, None)
    normalized = pipeline.normalizer.normalize(features)
    prediction = pipeline.classifier.predict(normalized)
    return prediction, normalized, features, windowed[..., 1:]

def run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model):
    main_template_path = os.path.abspath(os.path.join(fixtures, 'main.jinja2.cpp'))
    json_hpp_path = os.path.abspath(os.path.join(fixtures, 'json.hpp'))

    pipeline = Pipeline.load(model.pipeline)
    assert pipeline.windower.get_name() == 'Sample based'
    window_size = int(pipeline.windower.get_param_value_by_name('window_size'))

    code = downloadModel(model, Platforms.C)
    with TemporaryDirectory() as tmpdir_real:
        tmpdir = tmpdir_real
        zip_ref = zipfile.ZipFile(code)
        zip_ref.extractall(tmpdir)

        shutil.copy(json_hpp_path, tmpdir + '/json.hpp')

        with open(main_template_path, 'r') as file:
            main_template_str = file.read()
        main_template = Template(main_template_str)
        main_rendered = main_template.render({
            'csv_file_path': example_data_path,
            'datapoints_to_read': data_points_to_read,
            'window_size': window_size, #this is actually not needed irl, but behavior <= window_size is undefined in the cpp code
        })
        main_rendered_path = os.path.abspath(os.path.join(tmpdir, 'main.cpp'))
        with open(main_rendered_path, 'w') as file:
            file.write(Markup(main_rendered).unescape())

        main_binary_path = os.path.abspath(os.path.join(tmpdir, 'main.out'))
        subprocess.run(["g++", main_rendered_path, "-o", main_binary_path], check=True)
        process = subprocess.run([main_binary_path], stdout=subprocess.PIPE, text=True)
        output_dict = json.loads(process.stdout)

    return np.array(output_dict["predictions"]), \
        np.array(output_dict["normalized"]), \
        np.array(output_dict["features"]), \
        np.swapaxes(np.array(output_dict["windowed"]), 1, 2)


class TestMLDivergenceCPPPython(unittest.IsolatedAsyncioTestCase):
    """Test if whether python and cpp inference diverges.
    """

    @classmethod
    async def asyncSetUpClass(cls) -> None:
        setup_db_connection()
        found_model = await _models().find_one({'name': 'test_devicemotion_model'})
        model_id = found_model['_id']
        project = found_model['projectId']
        model = await get_model(model_id, project)

        fixtures = os.path.join(fixture_dir, 'test_divergence')
        example_data_path = os.path.abspath(os.path.join(fixtures, 'test_data.csv'))
        data_points_to_read = 375

        # predictions from the pipeline
        TestMLDivergenceCPPPython.res_ppl = run_prediction_pipeline(example_data_path, data_points_to_read, model)
        # predictions from the cpp model
        TestMLDivergenceCPPPython.res_cpp = run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model)

    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(TestMLDivergenceCPPPython.asyncSetUpClass())

    def setUp(self) -> None:
        self.prediction_ppl, self.normalized_ppl, self.features_ppl, self.windowed_ppl = TestMLDivergenceCPPPython.res_ppl
        self.prediction_cpp, self.normalized_cpp, self.features_cpp, self.windowed_cpp = TestMLDivergenceCPPPython.res_cpp

    async def test_prediction(self):
        """Test if cpp and python inference diverges with an example device motion dataset.
            You'll need to have the model 'test_devicemotion_model' in your database for this to work.
            The training data for the model can be found under tests/fixtures/test_divergence/
        """

        np.testing.assert_array_equal(self.prediction_ppl, self.prediction_cpp)

    async def test_normalizer(self):
        """uses a much higher atol (1e-6) than the other tests, because of the different feature extraction methods used
        """
        np.testing.assert_allclose(self.normalized_ppl, self.normalized_cpp, rtol=1e-05, atol=1e-06)

    async def test_feature_extractor(self):
        """uses a much higher atol (1e-3) than the other tests, because of the different feature extraction methods used
        """
        np.testing.assert_allclose(self.features_ppl, self.features_cpp, rtol=1e-05, atol=1e-03)

    async def test_windower(self):
        # cpp uses a circular buffer, so the order of the windows is different
        sorted_ppl = np.sort(self.windowed_ppl, axis=1)
        sorted_cpp = np.sort(self.windowed_cpp, axis=1)
        # use allclose instead of array_equal because of floating point errors
        np.testing.assert_allclose(sorted_ppl, sorted_cpp, rtol=1e-05, atol=1e-08)
