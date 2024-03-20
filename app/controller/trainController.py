from DataModels import PipelineRequest
from bson.objectid import ObjectId
from asyncTrain import calc
from DataModels import PipelineRequest
import json

def register_train(projectId: ObjectId, trainRequest: PipelineRequest):
    print("Train project: ", projectId)
    # res = trainAsync.delay(train_json, str(projectId))
    res = calc.delay(trainRequest.model_dump_json(by_alias=True), str(projectId))
    print("result: ", res.id)