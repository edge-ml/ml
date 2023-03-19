from fastapi import APIRouter
from app.routers import train, models, deploy

router = APIRouter()

# router.include_router(
#     config.router,
#     prefix="/config"
# )

router.include_router(
    train.router,
    prefix="/train"
)

router.include_router(
    models.router,
    prefix="/models"
)

router.include_router(
    deploy.router,
    prefix="/deploy"
)