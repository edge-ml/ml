from app.ml.Pipelines.Abstract.AbstractPipelineCreator import AbstractPipeLineCreator
from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep
from app.ml.Pipelines.Abstract.StepType import StepType
from app.ml.Pipelines.Categories.Classifier.TorchMultimodalCNN import TorchMultimodalCNN
from app.ml.Pipelines.Categories.Evaluation.LeaveOneGroupOut import LeaveOneGroupOut
from app.ml.Pipelines.Categories.Evaluation.TestTrainSplitEvaluation import TestTrainSplitEvaluation
from app.ml.Pipelines.Categories.FeatureExtraction.LogMelSensorExtractor import LogMelSensorExtractor
from app.ml.Pipelines.Categories.Normalizer.ChannelZNormalizer import ChannelZNormalizer
from app.ml.Pipelines.Categories.Windowing.SyncedTimeWindower import SyncedTimeWindower

# Step names must match the global categories (app.ml.Pipelines.getCategory),
# which the trainer uses to place each step; only the options differ.
AUDIO_CATEGORIES = [
    AbstractPipelineStep("Windowing", "Cuts the recordings into windows of a fixed duration", [SyncedTimeWindower], type=StepType.PRE),
    AbstractPipelineStep("Feature extraction", "What the model learns from", [LogMelSensorExtractor]),
    AbstractPipelineStep("Normalizer", "Defines how data is normalized", [ChannelZNormalizer]),
    AbstractPipelineStep("Classifier", "Classification of sound and sensor windows", [TorchMultimodalCNN]),
    AbstractPipelineStep("Evaluator", "Defines the evaluation strategy to be used.", [TestTrainSplitEvaluation, LeaveOneGroupOut], type=StepType.EVAL),
]


class AudioClassificationPipeline(AbstractPipeLineCreator):

    @classmethod
    def get_name(cls):
        return "Audio & Sensor Classification"

    @classmethod
    def get_description(cls):
        return ("Train on the sound of your recordings, on sensors, or on both together. "
                "Windows have a fixed duration; the models run on smartphones, in the browser and with PyTorch.")

    @staticmethod
    def get_categories():
        return AUDIO_CATEGORIES

    @classmethod
    def get_train_config(cls):
        # the wizard offers recordings (mediaSeries) for this pipeline only
        return {**super().get_train_config(), "usesRecordings": True}
