from celery import Celery
from DataModels import PipelineRequest
from ml.trainer import train
import asyncio
import json

from db.db import setup_db_connection

# Set up db
setup_db_connection()

celery_app = Celery("mlTrain", broker="amqp://guest:guest@127.0.0.1/")

@celery_app.task
# def trainAsync(pipelineRequest, project):
#     train(pipelineRequest, project)

@celery_app.task
def calc(pipelineRequest, project):
    pipelineRequest = PipelineRequest.model_validate(json.loads(pipelineRequest))
    print("req: ", pipelineRequest)
    asyncio.run(train(pipelineRequest, project))