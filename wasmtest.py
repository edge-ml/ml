import os
import zipfile
import joblib

from app.Deploy.Base import downloadModel
from app.ml.BaseConfig import Platforms

if __name__ == '__main__':
    fixture_dir = os.path.join(os.path.dirname(__file__), 'tests', 'fixtures')
    fixtures = os.path.join(fixture_dir, 'test_divergence')

    model = joblib.load(os.path.abspath(os.path.join(fixtures, 'dt_sample_maxnorm.joblib')))

    code = downloadModel(model, Platforms.WASM)
    dir = './outdir'
    zip_ref = zipfile.ZipFile(code)
    zip_ref.extractall(dir)