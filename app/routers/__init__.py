from fastapi import APIRouter
from routers import train, models, deploy

router = APIRouter()

# router.include_router(
#     config.router,
#     prefix="/config"
# )

router.include_router(
    train.router,
    prefix="/train",
    tags=["Training"]
)

router.include_router(
    models.router,
    prefix="/models",
    tags=["Models"]
)

router.include_router(
    deploy.router,
    prefix="/deploy",
    tags=["Deployment"]
)