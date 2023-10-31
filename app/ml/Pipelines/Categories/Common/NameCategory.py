from app.utils.parameter_builder import ParameterBuilder

from app.ml.Pipelines.Abstract.AbstractPipelineStep import AbstractPipelineStep

class NameCategory(AbstractPipelineStep):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.data_id = None

    @staticmethod
    def get_name():
        return "Model Name"

    @staticmethod
    def get_description():
        return "A name for your machine learning model"

    @staticmethod
    def get_platforms():
        return []

    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        pb.add_text("Name", "Name", "Each machine learning model needs a name", None, True, False)
        return pb.parameters
