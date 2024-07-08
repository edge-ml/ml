from app.db.models import get_project_models, delete_model, get_model, update_model


class ModelController:
    def __init__(self):
        pass

    async def get_model_by_id(self, project, model_id):
        res = await get_model(model_id, project)
        return res

    async def get_models(self, project):
        res = await get_project_models(project)
        return res

    async def delete_model(self, project, model_id):
        await delete_model(model_id, project)

    async def update_model(self, project, model_id, model):
        await update_model(project, model_id, model)