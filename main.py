
import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ml.training_manager import TrainingManager
from app.routers import ml

app = FastAPI()

# TODO: adapt to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    ml.router,
    prefix="/ml"
)

print("hi")
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup():
    loop = asyncio.get_event_loop()
    app.state.training_manager = TrainingManager(loop)

@app.on_event("shutdown")
async def shutdown():
    app.state.training_manager.destroy()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)