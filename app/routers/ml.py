from fastapi import APIRouter, Depends

from app.routers.dependencies import validate_user
from app.routers.models import models
from app.routers.train import train

router = APIRouter()
router.include_router(
    models.router,
    prefix='/models',
)
router.include_router(
    train.router,
    prefix='/train',
)

# TODO: /models?user={user}
# Return a list of models that were trained before by the user
@router.get("/userModels")  # userTrained / trained / created
async def models_user_created(user_id=Depends(validate_user)):
    return "List of models"
