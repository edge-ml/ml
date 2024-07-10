from fastapi import APIRouter
from app.routers import models, deploy

router = APIRouter()

router.include_router(
    models.router,
    prefix="/models",
    tags=["Model management"]
)

router.include_router(
    deploy.router,
    prefix="/deploy",
    tags=["Deploy a model"]
)