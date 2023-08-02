import os
from tempfile import TemporaryDirectory
import unittest
import zipfile
import numpy as np
from jinja2 import Template, Markup
import subprocess

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
    return prediction

def run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model):
    main_template_path = os.path.abspath(os.path.join(fixtures, 'main.jinja2.cpp'))

    pipeline = Pipeline.load(model.pipeline)
    assert pipeline.windower.get_name() == 'Sample based'
    window_size = int(pipeline.windower.get_param_value_by_name('window_size'))

    code = downloadModel(model, Platforms.C)
    with TemporaryDirectory() as tmpdir:
        zip_ref = zipfile.ZipFile(code)
        zip_ref.extractall(tmpdir)

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
        output = np.fromstring(process.stdout, sep="\n", dtype=int)

        return output
        

class TestMLDivergenceCPPPython(unittest.IsolatedAsyncioTestCase):
    """Test if whether python and cpp inference diverges.
    """

    def setUp(self) -> None:
        setup_db_connection()

    async def test_devicemotion_data(self):
        """Test if cpp and python inference diverges with an example device motion dataset.
            You'll need to have the model 'test_devicemotion_model' in your database for this to work.
            The training data for the model can be found under tests/fixtures/test_divergence/
        """
        found_model = await _models().find_one({'name': 'test_devicemotion_model'})

        model_id = found_model['_id']
        project = found_model['projectId']

        model = await get_model(model_id, project)

        fixtures = os.path.join(fixture_dir, 'test_divergence')
        example_data_path = os.path.abspath(os.path.join(fixtures, 'test_data.csv'))
        data_points_to_read = 375

        # predictions from the pipeline
        predictions_pipeline = run_prediction_pipeline(example_data_path, data_points_to_read, model)

        # predictions from the cpp model
        predictions_cpp = run_prediction_cpp(fixtures, example_data_path, data_points_to_read, model)

        np.testing.assert_array_equal(predictions_pipeline, predictions_cpp)
