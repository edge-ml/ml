from app.db.models import ModelDB
from app.DataModels.model import ModelStatus
from app.ml.PipelineExport.formats import formatsForStoredModel


def _with_formats(model):
    # models trained before formats were stored have formats=None
    if model.formats is None and model.trainStatus == ModelStatus.done:
        model.formats = formatsForStoredModel(model)
    return model


class ModelController:
    def __init__(self):
        self._model_db = ModelDB()

    def get_model_by_id(self, project, model_id):
        res = self._model_db.get_model(model_id, project)
        return _with_formats(res)

    def get_models(self, project):
        res = self._model_db.get_project_models(project)
        return [_with_formats(model) for model in res]

    def delete_model(self, project, model_id):
        return self._model_db.delete_model(model_id, project)

    def update_model(self, project, model_id, model):
        return self._model_db.update_model(model_id, project, model)