from fastapi import APIRouter
from app.routers import train, models, deploy

router = APIRouter()

router.include_router(
    train.router,
    prefix="/train",
    tags=["Train a model"]
)

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