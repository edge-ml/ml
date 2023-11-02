

from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus, set_model_data, set_train_error
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset
from app.DataProcessor.DataLoader.DataLoader import processDatasets


from app.ml.Pipelines.Categories.Evaluation import get_eval_by_name
from app.DataModels.trainRequest import TrainRequest

from app.ml.Pipeline import Pipeline
from app.DataModels.PipeLine import PipelineModel
from app.DataModels import PipelineRequest
import traceback

from app.ml.fit_to_pipeline import fit_to_pipeline


# def trainClassifier(windows, labels, modelInfo):
#     clf = model_map[modelInfo.classifier]()
#     # clf.hyperparameters = modelInfo.hyperparameters
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf


async def init_train(trainReq : PipelineRequest, id, project):
    try:
        await update_model_status(id, project, ModelStatus.training)
        # Get the datasets and lableings used for training
        datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
        labeling = await get_labeling(trainReq.labeling.id, project)

        # only keep selected timeseries from the datasets
        for ds in datasets:
            trainReqDs = next(reqDs for reqDs in trainReq.datasets if reqDs.id == ds.id)
            ds.timeSeries = [ts for ts in ds.timeSeries if ts.id in trainReqDs.timeSeries]

        if not all([len(x.timeSeries) == len(datasets[0].timeSeries) for x in datasets]):
            raise Exception('mismatching timeseries count in datasets')

        # only use selected labels in the map/naming
        selectedLabels = [label for label in labeling.labels if label.id not in trainReq.labeling.disabledLabelIDs]
        
        labelMap = {str(x.id): i for i, x in enumerate(selectedLabels)}
        maxIdx = max(labelMap.values())
        if trainReq.labeling.useZeroClass:
            labelMap["Zero"] = maxIdx+1

        labels = [x.name for x in selectedLabels]
        if trainReq.labeling.useZeroClass:
            labels.append("Zero")

        datasets_processed, datasetMetaData, samplingRate = processDatasets(datasets, trainReq.labeling, labelMap)


        pipeline, evaluator = fit_to_pipeline(trainReq, datasets_processed, datasetMetaData, labels)

        pipeline.persist()

        timeSeries = [x.name for x in datasets[0].timeSeries]
        # print(timeSeries)
        pipeline_data = pipeline.persist()
        pipeline_data["labels"] = labels
        pipeline_data["timeSeries"] = timeSeries
        pipeline_data["samplingRate"] = samplingRate
        await set_model_data(id, project, {"pipeline": PipelineModel.parse_obj(pipeline_data).dict(by_alias=True), "evaluator": evaluator.persist(), "timeSeries": timeSeries})
        await update_model_status(id, project, ModelStatus.done)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        await set_train_error(id, project, str(e))


async def train(req: PipelineRequest, project, background_tasks):
    data = req.dict(by_alias=True)
    modelName = req.selectedPipeline.steps[-1].options.parameters[0].value
    print("model_name: ", modelName)

    model = Model(name=modelName, pipeLineRequest=req, projectId=project)
    id = await add_model(model)

    background_tasks.add_task(init_train, req, id, project)
    return id