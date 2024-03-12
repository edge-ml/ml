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
import joblib

from Deploy.Base import downloadModel
from db.db import setup_db_connection
from db.models import get_model, _models
from ml.BaseConfig import Platforms
from ml.Pipeline import Pipeline

fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

def run_prediction_pipeline(csv_file_path, data_points_to_read, model, time_window_sep_interval = 30):
    pipeline = Pipeline.load(model.pipeline)

    data = np.genfromtxt(csv_file_path, delimiter=',', skip_header=0, max_rows=data_points_to_read)
    data = np.pad(data, ((0,0),(1,0)), mode='constant', constant_values=0) # add a zero column for the timestamp, as feature extraction expects it (and removes it)

    window_size = int(pipeline.windower.get_param_value_by_name('window_size'))
    if pipeline.windower.get_name() == 'Sample based':
        windowed = np.lib.stride_tricks.sliding_window_view(data, window_shape=(window_size, data.shape[-1])).squeeze(1)
    elif pipeline.windower.get_name() == 'Time based':
        lookbehind = window_size // time_window_sep_interval # n sample lookbehind
        windowed = []
        for i in range(0, data.shape[0]):
            windowed.append(data[max(0, i-lookbehind) : i+1])
    else:
        raise Exception('Unknown windower')

    features, _ = pipeline.featureExtractor.extract_features(windowed, None)
    normalized = pipeline.normalizer.normalize(features)
    prediction = pipeline.classifier.predict(normalized)

    # varying window size and windowing type leads to different output shapes
    first = len(windowed)
    second = np.max([len(sample) for sample in windowed])
    np_windowed = np.zeros((first, second, data.shape[-1] - 1))
    for i in range(first):
        window_len = len(windowed[i])
        for j in range(window_len):
            for k in range(data.shape[-1] - 1): # skip the timestamp
                np_windowed[i, j, k] = windowed[i][j][k + 1]

    return prediction, normalized, features, np_windowed

def run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model, time_window_sep_interval = 30):
    main_template_path = os.path.abspath(os.path.join(fixtures, 'main.jinja2.cpp'))
    json_hpp_path = os.path.abspath(os.path.join(fixtures, 'json.hpp'))

    pipeline = Pipeline.load(model.pipeline)
    window_size = int(pipeline.windower.get_param_value_by_name('window_size'))

    code = downloadModel(model, Platforms.C)
    with TemporaryDirectory() as tmpdir_real:
        tmpdir = tmpdir_real

        # unzip model
        zip_ref = zipfile.ZipFile(code)
        zip_ref.extractall(tmpdir)

        # json
        shutil.copy(json_hpp_path, tmpdir + '/json.hpp')

        # arduino polyfills for cpp:
        with open(tmpdir + '/model.hpp', 'r+') as file:
            polyfill = """
#include <chrono>
unsigned long millis() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(high_resolution_clock::now().time_since_epoch()).count();
}
"""
            original_content = file.read()
            file.seek(0, 0)
            file.write(polyfill)
            file.write(original_content)

        with open(main_template_path, 'r') as file:
            main_template_str = file.read()
        main_template = Template(main_template_str)
        main_rendered = main_template.render({
            'csv_file_path': example_data_path,
            'datapoints_to_read': data_points_to_read,
            'time_windowing': 1 if pipeline.windower.get_name() == 'Time based' else 0,
            'time_window_sep_interval': time_window_sep_interval,
            'window_size': window_size,
        })
        main_rendered_path = os.path.abspath(os.path.join(tmpdir, 'main.cpp'))
        with open(main_rendered_path, 'w') as file:
            file.write(Markup(main_rendered).unescape())

        main_binary_path = os.path.abspath(os.path.join(tmpdir, 'main.out'))
        subprocess.run(["g++", main_rendered_path, "-o", main_binary_path], check=True)
        process = subprocess.run([main_binary_path], stdout=subprocess.PIPE, text=True)
        output_dict = json.loads(process.stdout)

    # varying window size and windowing type leads to different output shapes
    first = len(output_dict["windowed"])
    second = np.max([len(sample) for sample in output_dict["windowed"]])
    third = np.max([[len(axis) for axis in sample] for sample in output_dict["windowed"]])
    np_windowed = np.zeros((first, second, third))
    for i in range(first):
        for j in range(second):
            window_len = len(output_dict["windowed"][i][j])
            for k in range(window_len):
                np_windowed[i, j, k] = output_dict["windowed"][i][j][k]

    return np.array(output_dict["predictions"]), \
        np.array(output_dict["normalized"]), \
        np.array(output_dict["features"]), \
        np.swapaxes(np_windowed, 1, 2)


class TestMLDivergenceCPPPythonBase(object):
    """Test if whether python and cpp inference diverges.
    """
    def setUp(self) -> None:
        self.prediction_ppl, self.normalized_ppl, self.features_ppl, self.windowed_ppl = self.res_ppl
        self.prediction_cpp, self.normalized_cpp, self.features_cpp, self.windowed_cpp = self.res_cpp

    def test_prediction(self):
        np.testing.assert_array_equal(self.prediction_ppl, self.prediction_cpp)

    def test_normalizer(self):
        """uses a much higher atol (1e-6) than the other tests, because of the different feature extraction methods used
        """
        np.testing.assert_allclose(self.normalized_ppl, self.normalized_cpp, rtol=1e-05, atol=1e-06)

    def test_feature_extractor(self):
        """uses a much higher atol (1e-3) than the other tests, because of the different feature extraction methods used
        """
        np.testing.assert_allclose(self.features_ppl, self.features_cpp, rtol=1e-05, atol=1e-03)

    def test_windower(self):
        # cpp uses a circular buffer, so the order of the windows is different
        sorted_ppl = np.sort(self.windowed_ppl, axis=1)
        sorted_cpp = np.sort(self.windowed_cpp, axis=1)
        # use allclose instead of array_equal because of floating point errors
        np.testing.assert_allclose(sorted_ppl, sorted_cpp, rtol=1e-05, atol=1e-08)

@unittest.skip("Use this test to check custom models.")
class TestMLDivergenceCPPPythonCustom(TestMLDivergenceCPPPythonBase, unittest.IsolatedAsyncioTestCase):
    """Test if cpp and python inference diverges.
        You'll need to have the model 'test_devicemotion_model' in your database for this to work.
        The training data for the model can be found under tests/fixtures/test_divergence/
    """
    @classmethod
    async def asyncSetUpClass(cls) -> None:
        setup_db_connection()
        found_model = await _models().find_one({'name': 'test_devicemotion_model'})
        model_id = found_model['_id']
        project = found_model['projectId']
        model = await get_model(model_id, project)
        cls.model = model

        fixtures = os.path.join(fixture_dir, 'test_divergence')
        example_data_path = os.path.abspath(os.path.join(fixtures, 'test_data.csv'))
        data_points_to_read = 375

        # predictions from the pipeline
        cls.res_ppl = run_prediction_pipeline(example_data_path, data_points_to_read, model)
        # predictions from the cpp model
        cls.res_cpp = run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model)

    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(TestMLDivergenceCPPPythonCustom.asyncSetUpClass())

class TestMLDivergenceCPPPythonSample(TestMLDivergenceCPPPythonBase, unittest.TestCase):
    """Decision Tree, sample based windowing, max normalization
    """
    @classmethod
    async def asyncSetUpClass(cls) -> None:
        fixtures = os.path.join(fixture_dir, 'test_divergence')

        model = joblib.load(os.path.abspath(os.path.join(fixtures, 'dt_sample_maxnorm.joblib')))

        example_data_path = os.path.abspath(os.path.join(fixtures, 'test_data.csv'))
        data_points_to_read = 375

        # predictions from the pipeline
        cls.res_ppl = run_prediction_pipeline(example_data_path, data_points_to_read, model)
        # predictions from the cpp model
        cls.res_cpp = run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model)

    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(TestMLDivergenceCPPPythonSample.asyncSetUpClass())

class TestMLDivergenceCPPPythonTime(TestMLDivergenceCPPPythonBase, unittest.TestCase):
    """Decision Tree, time based windowing, max normalization
    """
    @classmethod
    async def asyncSetUpClass(cls) -> None:
        fixtures = os.path.join(fixture_dir, 'test_divergence')

        model = joblib.load(os.path.abspath(os.path.join(fixtures, 'dt_time_maxnorm.joblib')))

        example_data_path = os.path.abspath(os.path.join(fixtures, 'test_data.csv'))
        data_points_to_read = 375

        # predictions from the pipeline
        cls.res_ppl = run_prediction_pipeline(example_data_path, data_points_to_read, model)
        # predictions from the cpp model
        cls.res_cpp = run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model)

    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(TestMLDivergenceCPPPythonTime.asyncSetUpClass())
