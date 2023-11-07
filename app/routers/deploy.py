from fastapi import APIRouter, Header
from app.db.models import get_model
from app.Deploy.Base import downloadModel
from app.ml.BaseConfig import Platforms
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.ml.Pipeline import Pipeline
from app.Deploy.Devices import DEVICES
from pydantic import BaseModel
from typing import List, Dict
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
    additionalSettings: Dict


router = APIRouter()
@router.get("/{model_id}/export/{format}")
async def export(format: str):
    pass

@router.get("/{model_id}/download/{format}")
async def dlmodel(model_id: str, format: Platforms, project: str = Header(...)):
    model = await get_model(model_id, project)
    code = downloadModel(model, format)
    # fileName = f"{model.name}_{format.name}.zip"
    # return StreamingResponse(code, media_type='application/zip', headers={
    #     f'Content-Disposition': 'attachment; filename="' + fileName + '"'
    # })

@router.get("/{model_id}")
async def deployConfig(model_id: str, project: str = Header(...)):
    return {"devices": [x.get_config() for x in  DEVICES], "parameters": Pipeline.get_parameters()}

@router.post("/{model_id}")
async def deploy(body : DeployRquest, model_id: str, project: str = Header(...)):
    device = get_device_by_name(body.device.name)
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
    model = await get_model(model_id, project)
    device = get_device_by_name(body.device.name)
    main_file_content = device.deploy(body.tsMap, body.parameters, body.additionalSettings, model)
    code = downloadModel(model, Platforms.C)

    zip_file = add_to_zip_file(code, main_file_content, f"{model.name}.ino")

    zip_file.seek(0)
    return StreamingResponse(zip_file, media_type="application/zip", headers={'Content-Disposition': f'attachment; filename={model.name}.zip'})

