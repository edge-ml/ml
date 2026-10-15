"""Models that can no longer be loaded (stored files missing, or saved by an
older edge-ml version, e.g. Keras 2 models) must answer downloads with a 409
and a message telling the user to retrain, instead of a 500."""
import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(__file__))
import test_torch_executorch  # noqa: E402,F401  (configures the environment before app imports)

from botocore.exceptions import ClientError  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from pydantic import BaseModel, ValidationError  # noqa: E402

from app.DataModels.model import ModelStatus  # noqa: E402
from app.Deploy import Base as deploy_base  # noqa: E402
from app.ml.BaseConfig import Platforms  # noqa: E402
from app.ml.Pipelines import ModelLoadError, modelLoadError  # noqa: E402
from app.routers import deploy, device  # noqa: E402
from test_device_api import KEYS  # noqa: E402

NO_SUCH_KEY = ClientError({"Error": {"Code": "NoSuchKey", "Message": "missing"}}, "GetObject")
KERAS_2 = TypeError("<class 'keras.src.models.sequential.Sequential'> could not be deserialized properly")


def validation_error():
    class Strict(BaseModel):
        name: str

    try:
        Strict()
    except ValidationError as e:
        return e


class TestModelLoadError(unittest.TestCase):

    def test_messages(self):
        self.assertIn("stored files are missing", str(modelLoadError(NO_SUCH_KEY)))
        self.assertIn("older edge-ml version", str(modelLoadError(KERAS_2)))
        self.assertIn("Retrain", str(modelLoadError(KERAS_2)))
        # an exception with a non-dict response attribute must not break it
        self.assertIn("older edge-ml version", str(modelLoadError(SimpleNamespace(response=object()))))

    def test_download_wraps_restore_failures(self):
        original = deploy_base.getPipeline
        deploy_base.getPipeline = lambda model: (_ for _ in ()).throw(KERAS_2)
        try:
            with self.assertRaises(ModelLoadError) as ctx:
                deploy_base.downloadModel(object(), Platforms.C)
            self.assertIs(ctx.exception.__cause__, KERAS_2)
        finally:
            deploy_base.getPipeline = original


class Patcher(unittest.TestCase):
    module = None

    def setUp(self):
        self.patches = {}

    def tearDown(self):
        for name, original in self.patches.items():
            setattr(self.module, name, original)

    def _patch(self, name, value):
        self.patches.setdefault(name, getattr(self.module, name))
        setattr(self.module, name, value)


class TestDeployDownload(Patcher):
    """The web app's model download (/ml/deploy/{id}/download/{format})."""
    module = deploy

    def setUp(self):
        super().setUp()
        app = FastAPI()
        app.include_router(deploy.router, prefix="/ml/deploy")
        self.client = TestClient(app)

    def get(self):
        return self.client.get("/ml/deploy/m1/download/C", headers={"project": "p1"})

    def test_unloadable_model_is_409(self):
        model = SimpleNamespace(name="old")
        self._patch("ModelDB", lambda: SimpleNamespace(get_model=lambda mid, pid: model))
        for error in [NO_SUCH_KEY, KERAS_2]:
            with self.subTest(error=type(error).__name__):
                self._patch("downloadModel", lambda m, f, e=error: (_ for _ in ()).throw(modelLoadError(e)))
                res = self.get()
                self.assertEqual(res.status_code, 409, res.text)
                self.assertIn("Retrain", res.json()["detail"])

    def test_unreadable_model_document_is_409(self):
        def get_model(mid, pid):
            raise validation_error()

        self._patch("ModelDB", lambda: SimpleNamespace(get_model=get_model))
        res = self.get()
        self.assertEqual(res.status_code, 409, res.text)
        self.assertIn("older edge-ml version", res.json()["detail"])


class TestDeviceDownload(Patcher):
    """The libraries' model downloads (/ml/device/{key}/models/{id}/...)."""
    module = device

    def setUp(self):
        super().setUp()
        self._patch("get_auth_db", lambda: SimpleNamespace(
            client={device.DEVICE_API_DB_NAME: {device.DEVICE_API_COLLNAME: KEYS}}))
        app = FastAPI()
        app.include_router(device.router, prefix="/ml/device")
        self.client = TestClient(app)

    def test_unloadable_model_is_409(self):
        model = SimpleNamespace(trainStatus=ModelStatus.done, formats=["ONNX", "EXECUTORCH"], name="old", id="m1")
        self._patch("_get_model", lambda mid, project: model)
        self._patch("getPipeline", lambda m: (_ for _ in ()).throw(NO_SUCH_KEY))
        for path in ["onnx/manifest.json", "executorch/manifest.json"]:
            with self.subTest(path=path):
                res = self.client.get(f"/ml/device/READ/models/m1/{path}")
                self.assertEqual(res.status_code, 409, res.text)
                self.assertIn("stored files are missing", res.json()["detail"])


if __name__ == "__main__":
    unittest.main()
