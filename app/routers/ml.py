# from fastapi import APIRouter, Depends

# from routers.dependencies import validate_user
# from routers.models import models
# from routers.train import train
# from routers.deploy import deploy

# router = APIRouter()
# router.include_router(
#     models.router,
#     prefix='/models',
# )
# router.include_router(
#     train.router,
#     prefix='/train',
# )
# router.include_router(
#     deploy.router,
#     prefix='/deploy',
# )

# # TODO: /models?user={user}
# # Return a list of models that were trained before by the user
# @router.get("/userModels")  # userTrained / trained / created
# async def models_user_created(user_data=Depends(validate_user)):
#     return "List of models"
