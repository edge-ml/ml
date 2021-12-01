
import uvicorn

from fastapi import FastAPI
from routers import models



app = FastAPI()

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