import json
from io import BytesIO

import numpy as np
import torch
from torch import nn
from bson.objectid import ObjectId

from app.codegen.inference.InferenceFormats import InferenceFormats
from app.ml.BaseConfig import Platforms
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier.BaseClassififer import BaseClassififer
from app.dataLoader import DATASTORE


class TorchNeuralNetwork(BaseClassififer):
    """Base class for PyTorch classifiers.

    Mirrors the persist/restore contract of the Keras NeuralNetwork class, but
    additionally stores the network architecture in the model state (Mongo) so
    the module can be rebuilt before loading the weights from the DATASTORE.
    Models output raw logits; predict returns class indices.
    """

    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None
        self.model: nn.Module = None
        self.arch: dict = None

    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        return pb.parameters

    @staticmethod
    def get_name():
        return "PyTorch Neural Network Classifier"

    @staticmethod
    def get_description():
        return "Abstract wrapper for PyTorch neural network classifiers, not intended for actual use."

    @staticmethod
    def get_platforms():
        # Runs server-side (PYTHON) and exports to mobile via ExecuTorch (.pte).
        # Actual export eligibility still depends on the full pipeline
        # (see PipelineExport.formats.computeFormats); this advertises the
        # classifier's capability so the wizard can surface it.
        return [InferenceFormats.PYTHON, Platforms.EXECUTORCH]

    def build_arch(self, input_shape, num_classes) -> dict:
        raise NotImplementedError()

    @staticmethod
    def build_model(arch) -> nn.Module:
        raise NotImplementedError()

    def _get_param(self, name, default, cast=float):
        try:
            value = self.get_param_value_by_name(name)
        except KeyError:
            return default
        if value is None or value == "":
            return default
        return cast(float(value))

    def fit(self, X_train, y_train):
        X = torch.as_tensor(np.asarray(X_train, dtype=np.float32))
        y = torch.as_tensor(np.asarray(y_train, dtype=np.int64))
        num_classes = int(y.max().item()) + 1

        self.arch = self.build_arch(list(X.shape[1:]), num_classes)
        self.model = self.build_model(self.arch)

        epochs = self._get_param("epochs", 50, int)
        learning_rate = self._get_param("learning_rate", 1e-3, float)
        batch_size = self._get_param("batch_size", 32, int)

        dataset = torch.utils.data.TensorDataset(X, y)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in loader:
                optimizer.zero_grad()
                loss = criterion(self.model(batch_X), batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * batch_X.shape[0]
            print(f"Epoch {epoch + 1}/{epochs} - loss: {epoch_loss / len(dataset):.6f}")
        self.model.eval()

    def predict(self, X_test):
        X = torch.as_tensor(np.asarray(X_test, dtype=np.float32))
        self.model.eval()
        with torch.no_grad():
            logits = self.model(X)
        return torch.argmax(logits, dim=-1).numpy()

    def export_torch_module(self) -> nn.Module:
        return self.model

    def get_state(self):
        return {"data_id": self.data_id, "arch": json.dumps(self.arch)}

    def as_file(self):
        buffer = BytesIO()
        torch.save(self.model.state_dict(), buffer)
        buffer.seek(0)
        return {"name": f"{self.get_name()}.pt", "buffer": buffer}

    def persist(self):
        self.data_id = ObjectId()
        buffer = BytesIO()
        torch.save(self.model.state_dict(), buffer)
        buffer.seek(0)
        DATASTORE.saveObj(str(self.data_id), buffer)
        return super().persist()

    def restore(self, config):
        self.data_id = config.state["data_id"]
        self.arch = json.loads(config.state["arch"])
        self.model = self.build_model(self.arch)
        binModel = DATASTORE.loadObj(id=str(self.data_id))
        self.model.load_state_dict(torch.load(binModel, map_location="cpu"))
        self.model.eval()
        super().restore(config)
