from fastapi import APIRouter, Header
from app.db.models import get_model
from app.Deploy.Base import downloadModel
from app.ml.BaseConfig import Platforms
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.ml.Pipeline import Pipeline
from app.Deploy import DEPLOY_DEVICES
from pydantic import BaseModel
from typing import List
from app.DataModels.parameter import Parameter
from app.Deploy.Devices import get_device_by_name
from app.utils.zipfile import add_to_zip_file
import requests
from app.internal.config import FIRMWARE_COMPILE_URL

class tsMapComponent(BaseModel):
    sensor_id: int
    component_id: int


class ComponentModel(BaseModel):
    name: str
    dtype: str

class SensorModel(BaseModel):
    name: str
    components: List[ComponentModel]

class Device(BaseModel):
    name: str
    sensors: List[SensorModel]

class DeployRquest(BaseModel):
    tsMap: List[tsMapComponent]
    parameters: List[Parameter]
    device: Device


router = APIRouter()
@router.get("/{model_id}/export/{format}")
async def export(format: str):
    pass
    # token = user_data[1]

    # timeseries = model.timeseries if model.timeseries else ["Sensor_A", "Sensor_B", "Sensor_C"]
    # labels = model.labels if model.labels else ["label1", "label2"]
    # wsize =  model.window_size if model.window_size else "<WINDOW_SIZE>"

    # form = InferenceFormats.from_str(format)
    # platform = next(x for x in platforms if form in x.supported_formats())

    # label_defs = fetch_label_definition(project_id, token)
    # label_names = [ (next(x for x in label_defs["labelTypes"] if x["_id"] == labelId))["name"] for labelId in labels ]

    # return platform.codegen(
    #     window_size = wsize,
    #     timeseries = timeseries,
    #     labels = label_names,
    #     format = form,
    #     scaler = model.scaler,
    #     windowing_mode = model.windowing_mode
    # )

@router.get("/{model_id}/download/{format}")
async def dlmodel(model_id: str, format: Platforms, project: str = Header(...)):
    model = await get_model(model_id, project)
    code = downloadModel(model, format)
    print(code)
    fileName = f"{model.name}_{format.name}.zip"
    return StreamingResponse(code, media_type='application/zip', headers={
        f'Content-Disposition': 'attachment; filename="' + fileName + '"'
    })

@router.get("/{model_id}")
async def deployConfig(model_id: str, project: str = Header(...)):
    return {"devices": [x.get_config() for x in  DEPLOY_DEVICES], "parameters": Pipeline.get_parameters()}

@router.post("/{model_id}")
async def deploy(body : DeployRquest, model_id: str, project: str = Header(...)):
    device = get_device_by_name(body.device.name)()
    main_file_content = device.deploy(body.tsMap, body.parameters)

    model = await get_model(model_id, project)
    code = downloadModel(model, Platforms.C)

    zip_file = add_to_zip_file(code, main_file_content, "main.ino")
    file_data = {'file': ('example.zip', zip_file)}
    url = f"{FIRMWARE_COMPILE_URL}compile/nicla"
    response = requests.post(url, files=file_data)
    print(response.content)
    return StreamingResponse(iter([response.content]), media_type="application/octet-stream")

@router.post("/{model_id}/download")
async def deploy(body : DeployRquest, model_id: str, project: str = Header(...)):
    device = get_device_by_name(body.device.name)()
    main_file_content = device.deploy(body.tsMap, body.parameters)

    model = await get_model(model_id, project)
    code = downloadModel(model, Platforms.C)

    zip_file = add_to_zip_file(code, main_file_content, "main.ino")

    zip_file.seek(0)
    return StreamingResponse(zip_file, media_type="application/zip", headers={'Content-Disposition': f'attachment; filename={model.name}.zip'})

