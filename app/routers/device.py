"""Device-API routes for the edge-ml JavaScript library.

Authenticated with the project's device API key (the same read/write keys the
dataset-store upload routes use), so a browser or Node app can train a model
and download it as ONNX without a user session:

    GET  /ml/device/{api_key}/pipelines                      available steps/options (read)
    POST /ml/device/{api_key}/train                          start training (write)
    GET  /ml/device/{api_key}/models                         list models (read)
    GET  /ml/device/{api_key}/models/{model_id}              training status (read)
    GET  /ml/device/{api_key}/models/{model_id}/onnx/manifest.json
    GET  /ml/device/{api_key}/models/{model_id}/onnx/model.onnx
"""
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from starlette.concurrency import run_in_threadpool

from app.db.db import get_auth_db
from app.db.datasets import get_project_datasets_meta
from app.db.labelings import get_project_labelings
from app.db.models import ModelDB
from app.internal.config import DEVICE_API_COLLNAME, DEVICE_API_DB_NAME
from app.DataModels.model import ModelStatus
from app.ml.device_train import DeviceTrainError, DeviceTrainRequest, buildPipelineRequest, modelSummary
from app.ml.Pipelines import PIPELINES_CONFIG, getPipeline
from app.ml.PipelineExport.Onnx.support import OnnxExportError
from app.ml.trainer import train
from app.ml.validation import preflight_train
from app.utils.jsonEncoder import JSONEncoder

router = APIRouter()
modelDB = ModelDB()


class requireApiKey:
    """access 'read' accepts read and write keys, 'write' only write keys
    (a write key grants more than a read key)."""

    def __init__(self, access: str):
        self.access = access

    async def __call__(self, api_key: str) -> str:
        col = get_auth_db().client[DEVICE_API_DB_NAME][DEVICE_API_COLLNAME]
        doc = await col.find_one({"writeApiKey": api_key})
        if doc is None and self.access == "read":
            doc = await col.find_one({"readApiKey": api_key})
        if doc is None:
            if self.access == "write" and await col.find_one({"readApiKey": api_key}):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Used Api Key does not grant write access")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
        return str(doc["projectId"])


def _json(obj) -> Response:
    return Response(json.dumps(obj, cls=JSONEncoder), media_type="application/json")


def _get_model(model_id: str, project: str):
    try:
        doc = modelDB._collection.find_one({"_id": ObjectId(model_id), "projectId": ObjectId(project)})
    except InvalidId:
        doc = None
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")
    return modelDB.get_model(model_id, project)


def _onnx_ready_pipeline(model):
    if model.trainStatus != ModelStatus.done:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"Model is not trained yet (status: {model.trainStatus.value}).")
    if "ONNX" not in (model.formats or []):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="This model cannot be exported to ONNX. Train it with sample-based windowing, the "
                   "SimpleFeatureExtractor or raw time-series, a MinMax/Z normalizer and a Decision Tree, "
                   "Random Forest or PyTorch classifier.",
        )
    return getPipeline(model)


@router.get("/{api_key}/pipelines")
async def device_pipelines(project: str = Depends(requireApiKey("read"))):
    return PIPELINES_CONFIG


@router.post("/{api_key}/train")
async def device_train(
    body: DeviceTrainRequest,
    background_tasks: BackgroundTasks,
    project: str = Depends(requireApiKey("write")),
):
    datasets = await get_project_datasets_meta(project)
    labelings = await get_project_labelings(project)
    try:
        req = buildPipelineRequest(body, datasets, labelings)
    except DeviceTrainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    check = await preflight_train(req, project)
    if not check.get("valid", False):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="; ".join(f"{e['step']}: {e['message']}" for e in check.get("errors", [])),
        )

    model_id = await train(req, project=project, background_tasks=background_tasks)
    return _json({"id": str(model_id), "warnings": check.get("warnings", [])})


@router.get("/{api_key}/models")
async def device_models(project: str = Depends(requireApiKey("read"))):
    return _json([modelSummary(m) for m in modelDB.get_project_models(project)])


@router.get("/{api_key}/models/{model_id}")
async def device_model(model_id: str, project: str = Depends(requireApiKey("read"))):
    return _json(modelSummary(_get_model(model_id, project)))


@router.get("/{api_key}/models/{model_id}/onnx/manifest.json")
async def device_onnx_manifest(model_id: str, project: str = Depends(requireApiKey("read"))):
    from app.ml.PipelineExport.Onnx.OnnxCompiler import buildOnnxManifest

    model = _get_model(model_id, project)
    pipeline = _onnx_ready_pipeline(model)
    return _json(buildOnnxManifest(pipeline.options, model))


@router.get("/{api_key}/models/{model_id}/onnx/model.onnx")
async def device_onnx_model(model_id: str, project: str = Depends(requireApiKey("read"))):
    from app.ml.PipelineExport.Onnx.OnnxCompiler import buildOnnxModel

    model = _get_model(model_id, project)
    pipeline = _onnx_ready_pipeline(model)
    try:
        # tracing / conversion is CPU-bound — keep it off the event loop
        model_bytes = await run_in_threadpool(buildOnnxModel, pipeline.options, model)
    except OnnxExportError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return Response(model_bytes, media_type="application/octet-stream", headers={
        "Content-Disposition": f'attachment; filename="{model.name}.onnx"'
    })
