from fastapi import APIRouter
from app.routers import models, deploy, train

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

router.include_router(
    train.router,
    prefix="/train",
    tags=["Train a model"]
)