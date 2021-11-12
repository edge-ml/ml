from fastapi import APIRouter

router = APIRouter()

@router.get("/model/")
async def model():
    return [] #TODO: return the list of models available for training and the related hyperparameters


@router.post("/model/{model_id}")
async def model_train():
    return "id of the model to train" #TODO return the trained model


@router.get("/model/trained")
async def model_trained():
    return "trained models list" #TODO returns the list of trained models

@router.get("/model/trained/{trained_model_id}")
async def model_trained():
    return "trained models" #TODO returns the trained model
