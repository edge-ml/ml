from app.db.models import get_project_models, delete_model

async def get_models(projectId):
    res = await get_project_models(projectId)
    print(res)
    return res