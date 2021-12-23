
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import models

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
    models.router,
    prefix="/ml"
)

print("hi")
@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)