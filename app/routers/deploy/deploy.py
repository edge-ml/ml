from typing import List
from fastapi import APIRouter, Depends, Request, Response

from app.db.models import get_model
from app.db.models.model import Model
from app.models.edge_model import EdgeModelPlatform
from app.routers.dependencies import validate_model

router = APIRouter()

@router.get("/{model_id}")
async def deployment(model=Depends(validate_model)):
    return {
        'platforms': model.edge_model.get_platforms(),
    }

@router.get("/{model_id}/export/{platform}")
async def export(platform: str, model: Model = Depends(validate_model)):
    timeseries = model.timeseries if model.timeseries else ["Sensor_A", "Sensor_B", "Sensor_C"]
    labels = model.labels if model.labels else []
    wsize =  model.window_size if model.window_size else "<WINDOW_SIZE>"

    print(platform + " Platform: " + str(EdgeModelPlatform.from_str(platform)))
    
    if (EdgeModelPlatform.from_str(platform) == EdgeModelPlatform.PYTHON):
        tadd = ""
        for ts in timeseries:
            tadd = tadd + '\n\tp.add_datapoint(\'{ts}\', get{ts}())'.format(ts = ts)

        code = """import time
from edgeml.predictor import Predictor, PredictorError
import pickle

model = # pickle.loads(...) # load model file with pickle

p = Predictor(
    model,
    {timeseries_list},
    {wsize},
    {labels}
)

while True:
{timeseries_add}

    try:
        print(p.predict())
    except PredictorError:
        pass
    
    time.sleep(0.25)
""".format(
            wsize=wsize,
            timeseries_list=str(timeseries),
            labels=str(labels),
            timeseries_add=tadd
        )

        return {
            'code': code,
            'model': True
        }

    return {
        'code': model.edge_model.export(EdgeModelPlatform.from_str(platform))
    }

@router.get("/{model_id}/download")
async def dlmodel(model=Depends(validate_model)):
    return Response(content=model.pickled_edge_model, media_type="application/octet-stream")