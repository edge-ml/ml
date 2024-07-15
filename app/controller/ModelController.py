from app.db.models import ModelDB


class ModelController:
    def __init__(self):
        self._model_db = ModelDB()

    def get_model_by_id(self, project, model_id):
        res = self._model_db.get_model(model_id, project)
        return res

    def get_models(self, project):
        res = self._model_db.get_project_models(project)
        return res

    def delete_model(self, project, model_id):
        return self._model_db.delete_model(model_id, project)

    def update_model(self, project, model_id, model):
        return self._model_db.update_model(model_id, project, model)