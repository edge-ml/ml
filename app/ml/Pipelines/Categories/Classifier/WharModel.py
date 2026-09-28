from torch import nn

from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier.TorchNeuralNetwork import TorchNeuralNetwork

# whar-models (teco-kit) is installed as a library in the ml image (see
# Dockerfile / requirements). Guarded so this module still imports if the library
# is absent in a dev checkout — the classifier just won't have any architectures
# to offer. In the deployed image it is present.
try:
    from whar_models import (
        WHARModelID,
        build_model as _whar_build_model,
        get_model_spec,
    )

    # Architectures with hard input constraints that don't fit edge-ml's
    # The neural (torch) architectures only; the classical ones (knn/rf/svm) are
    # sklearn + tsfresh and out of scope for this torch-trained classifier.
    # deepsense/global_fusion have channel-count constraints (deepsense needs an
    # even count, global_fusion needs >= 6); rather than exclude them platform-
    # wide, they're offered here and the wizard hides them only when the selected
    # dataset's channel count is incompatible (see CHANNEL_CONSTRAINED_ARCHS in
    # the frontend and the preflight guardrail in validation.py).
    _NEURAL_MODEL_IDS = [
        m.value for m in WHARModelID if get_model_spec(m).framework == "torch"
    ]
except Exception:  # pragma: no cover - library missing in a bare dev env
    WHARModelID = None
    _whar_build_model = None
    _NEURAL_MODEL_IDS = []

_DEFAULT_MODEL_ID = "cnn_har"


class _ChannelsFirst(nn.Module):
    """edge-ml windows are channels-last (batch, window, channels); whar-models
    expect channels-first (batch, channels, window). Permute at the boundary."""

    def forward(self, x):
        return x.permute(0, 2, 1)


class WharModel(TorchNeuralNetwork):
    """Wraps a standard WHAR architecture from the whar-models library as an
    edge-ml PyTorch classifier. The specific architecture is chosen via the
    `model_id` dropdown; edge-ml's inherited training loop trains it, and it can
    be exported to smartphones via ExecuTorch (.pte) where the architecture's ops
    can be lowered (recurrent/attention models fall back to server-only)."""

    def __init__(self, parameters=[]):
        super().__init__(parameters)

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_selection(
            "model_id", "Architecture",
            "Which standard WHAR architecture (from the whar-models library) to train.",
            _NEURAL_MODEL_IDS or [_DEFAULT_MODEL_ID], _DEFAULT_MODEL_ID,
            False, True, False
        )
        pb.add_number(
            "epochs", "Training Epochs", "Number of passes over the training data.",
            1, 500, 50, 1
        )
        pb.add_number(
            "learning_rate", "Learning Rate", "Learning rate of the Adam optimizer.",
            0.00001, 0.1, 0.001, 0.00001, True, True
        )
        pb.add_number(
            "batch_size", "Batch Size", "Number of windows per training batch.",
            4, 512, 32, 1
        )
        return pb.parameters

    @staticmethod
    def get_name():
        return "WHAR Model"

    @staticmethod
    def get_description():
        return "Standard Human Activity Recognition architectures from the whar-models library (DeepConvLSTM, TinyHAR, CNN-HAR, SA-HAR and more), selectable via the Architecture dropdown. Best used with the 'Raw Time-Series (Sensors only)' feature extraction. Can be exported to smartphones via ExecuTorch (.pte) where the chosen architecture supports it."

    def _get_model_id(self):
        try:
            value = self.get_param_value_by_name("model_id")
        except KeyError:
            value = None
        return value or _DEFAULT_MODEL_ID

    def build_arch(self, input_shape, num_classes):
        # input_shape is channels-last [timesteps, channels].
        return {
            "type": "whar",
            "model_id": self._get_model_id(),
            "input_channels": int(input_shape[1]),
            "window_length": int(input_shape[0]),
            "num_classes": int(num_classes),
        }

    @staticmethod
    def build_model(arch):
        if _whar_build_model is None:
            raise RuntimeError("whar-models library is not installed in this environment")
        module = _whar_build_model(
            WHARModelID(arch["model_id"]),
            input_channels=int(arch["input_channels"]),
            window_length=int(arch["window_length"]),
            num_classes=int(arch["num_classes"]),
        )
        # whar-models take (batch, channels, timesteps); edge-ml feeds
        # (batch, timesteps, channels), so permute first.
        return nn.Sequential(_ChannelsFirst(), module)
