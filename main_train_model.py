import uvicorn
import argparse
from app.routers import train


parser = argparse.ArgumentParser(description="Run the ml service")

parser.add_argument('--env', default="dev", choices=["dev", "docker"])
parser.add_argument('--workers', type=int, default=20)
args = parser.parse_args()
env = args.env
workers = args.workers
print("num_workers", workers)

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.db import setup_db_connection
from app.routers import router

app = FastAPI()

# TODO: adapt to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

router.include_router(
    train.router,
    prefix="/train",
    tags=["Train a model"]
)

@app.on_event("startup")
async def startup():
    setup_db_connection()


if __name__ == "__main__":
    if env == "dev":
        uvicorn.run("main:app", host="0.0.0.0", port=3006, reload=True)
    if env == "docker":
        uvicorn.run("main:app", host="0.0.0.0", port=3006, workers=workers)
