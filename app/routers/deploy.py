from fastapi import APIRouter, Header
from app.db.models import get_model
from app.Deploy.Base import deployModel

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
async def dlmodel(model_id: str, format: str, project: str = Header(...)):
    model = await get_model(model_id, project)
    deployModel(model)
