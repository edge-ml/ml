

from DataModels.model import Model
from db.models import add_model, update_model_status, ModelStatus, set_model_data, set_train_error
from db.labelings import get_labeling
from db.datasets import get_dataset
from DataProcessor.DataLoader.DataLoader import processDatasets
from DataModels.PipelineRequest import PipelineStep, PipelineStepOption


from ml.Pipelines.Categories.Evaluation import get_eval_by_name
from DataModels.trainRequest import TrainRequest

from ml.Pipeline import Pipeline
from DataModels.PipeLine import PipelineModel
from DataModels import PipelineRequest
from ml.Pipelines.PipelineContainer import PipelineContainer
import traceback

from ml.fit_to_pipeline import fit_to_pipeline, buildPipeline, getEvaluator


# def trainClassifier(windows, labels, modelInfo):
#     clf = model_map[modelInfo.classifier]()
#     # clf.hyperparameters = modelInfo.hyperparameters
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf




async def init_train(trainReq : PipelineRequest, model : Model, id, project):
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

        print(selectedLabels)
        labels = [x.name for x in selectedLabels]
        if trainReq.labeling.useZeroClass:
            labels.append("Zero")

        datasets_processed, datasetMetaData, samplingRate = processDatasets(datasets, trainReq.labeling, labelMap)


        # pipeline, evaluator = fit_to_pipeline(trainReq, datasets_processed, datasetMetaData, labels)

        pipeline : Pipeline = buildPipeline(trainReq)
        evaluator = getEvaluator(trainReq)

        data = PipelineContainer(datasets_processed, None, datasetMetaData)

        performance = pipeline.eval(data, labels)

        timeSeries = [x.name for x in datasets[0].timeSeries]


        for i, cs in enumerate(pipeline.persist()):
            model.pipeline.selectedPipeline.steps[i].options = cs
        

        model.timeSeries = timeSeries
        model.samplingRate = samplingRate
        model.labels = [x.dict(by_alias=True) for x in selectedLabels] + ([{"name": "Zero", "color": "#ffffff"}] if trainReq.labeling.useZeroClass else [])
        await set_model_data(id, project, model.dict(by_alias=True))
        # ml_data = {}
        # ml_data["concreteSteps"] = pipeline.persist()
        # ml_data["labels"] = [x.dict(by_alias=True) for x in selectedLabels] + ([{"name": "Zero", "color": "#ffffff"}] if trainReq.labeling.useZeroClass else [])
        # ml_data["timeSeries"] = timeSeries
        # ml_data["samplingRate"] = samplingRate
        # ml_data["performance"] = performance
        # await set_model_data(id, project, ml_data)
        await update_model_status(id, project, ModelStatus.done)
    except Exception as e:
        print("Train_error!")
        print(e)
        print(traceback.format_exc())
        await set_train_error(id, project, str(e))


async def train(req: PipelineRequest, project, background_tasks):
    data = req.dict(by_alias=True)
    model = Model(name=req.name, pipeline=req, projectId=project)
    id = await add_model(model)
    background_tasks.add_task(init_train, req, model, id, project)
    return id