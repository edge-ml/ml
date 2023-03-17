from fastapi import APIRouter
from app.routers import config
from app.routers import train

router = APIRouter()

router.include_router(
    config.router,
    prefix="/config"
)

router.include_router(
    train.router,
    prefix="/train"
)