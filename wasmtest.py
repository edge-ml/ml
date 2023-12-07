import asyncio
import os
import zipfile
import joblib

from app.Deploy.Base import downloadModel
from app.ml.BaseConfig import Platforms

from app.db.db import setup_db_connection
from app.db.models import get_model

import requests
from app.internal.config import FIRMWARE_COMPILE_URL

async def main():
    setup_db_connection()

    fixture_dir = os.path.join(os.path.dirname(__file__), 'tests', 'fixtures')
    fixtures = os.path.join(fixture_dir, 'test_divergence')

    # model = joblib.load(os.path.abspath(os.path.join(fixtures, 'dt_sample_maxnorm.joblib')))
    model = await get_model("6571275241821119c7fd303d", "65682ecf45d9a3b849ead672")

    code = downloadModel(model, Platforms.WASM)

    file_data = {'file': ('example.zip', code)}
    
    url = f"{FIRMWARE_COMPILE_URL}compile/WASM-single-file"
    response = requests.post(url, files=file_data)

    dir = './outdir'
    
    with open(dir + '/model.js', 'wb') as file:
        file.write(response.content)

    zip_ref = zipfile.ZipFile(code)
    zip_ref.extractall(dir)

    # in the firmware compile repo:
    # emcc outdir/model.cpp -o outdir/model.js -sMODULARIZE -s EXPORTED_FUNCTIONS="['_predict', '_add_datapoint']" -s EXPORTED_RUNTIME_METHODS="['cwrap']"
    ############

if __name__ == '__main__':
    asyncio.run(main())