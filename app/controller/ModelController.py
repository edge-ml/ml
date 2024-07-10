from app.db.models import ModelDB


class ModelController:
    def __init__(self):
        self._model_db = ModelDB()

    async def get_model_by_id(self, project, model_id):
        res = await self._model_db.get_model(model_id, project)
        return res

    def get_models(self, project):
        res = self._model_db.get_project_models(project)
        return res

    async def delete_model(self, project, model_id):
        await self._model_db.delete_model(model_id, project)

    async def update_model(self, project, model_id, model):
        await self._model_db.update_model(project, model_id, model)