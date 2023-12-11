import uvicorn
import argparse
parser = argparse.ArgumentParser(description="Run the ml service")

parser.add_argument('--env', default="dev", choices=["dev", "docker"])
args = parser.parse_args()
env = args.env

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

app.include_router(
    router,
    prefix="/ml"
)

@app.on_event("startup")
async def startup():
    setup_db_connection()


if __name__ == "__main__":
    if env == "dev":
        uvicorn.run("main:app", host="0.0.0.0", port=3003, reload=True)
    if env == "docker":
        uvicorn.run("main:app", host="0.0.0.0", port=3003, workers=20)
