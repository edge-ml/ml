import numpy as np


from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus, set_model_data
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset


from app.DataProcessor.DataPreProcessor import getDatasetWindows, calculateFeatures
from app.DataProcessor.DataLoader.DataLoader import processDataset
from app.ml.Evaluation import get_eval_by_name, BaseEvaluation
from app.DataModels.trainRequest import TrainRequest

from app.ml.Classifier import get_classifier_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Windowing import get_windower_by_name
from app.ml.FeatureExtraction import get_feature_extractor_by_name
from app.ml.Pipeline import Pipeline
from app.DataModels.PipeLine import PipelineModel
import traceback



# def trainClassifier(windows, labels, modelInfo):
#     clf = model_map[modelInfo.classifier]()
#     # clf.hyperparameters = modelInfo.hyperparameters
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf


async def init_train(trainReq : TrainRequest, id, project):
    try:
        print("init training")
        await update_model_status(id, project, ModelStatus.preprocessing)
        # Get the datasets and lableings used for training
        datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
        labeling = await get_labeling(trainReq.labeling.id, project)
        useZeroClass = trainReq.labeling.useZeroClass
        
        labelMap = {str(x.id): i for i, x in enumerate(labeling.labels)}
        maxIdx = max(labelMap.values())
        print(labelMap.keys(), maxIdx)
        if useZeroClass:
            labelMap["Zero"] = maxIdx+1

        print(labelMap)
        print("datasets: ", len(datasets))

        datasets_processed = [processDataset(dataset, trainReq.labeling.id, labelMap, useZeroClass) for dataset in datasets]
        labels = [x.name for x in labeling.labels]
        if useZeroClass:
            labels.append("Zero")
        print("LABELS: ", labels)

        await update_model_status(id, project, ModelStatus.fitting_model)
        evaluator = get_eval_by_name(trainReq.evaluation.name)(trainReq.windowing, trainReq.featureExtractor, trainReq.normalizer, trainReq.classifier, datasets_processed, labels, trainReq.evaluation)
        pipeline : Pipeline = evaluator.train_eval()

        print("pipeline")
        print(pipeline.persist())

        timeSeries = [x.name for x in datasets[0].timeSeries]
        print(timeSeries)
        pipeline_data = pipeline.persist()
        pipeline_data["labels"] = labels
        pipeline_data["timeSeries"] = timeSeries
        await set_model_data(id, project, {"pipeline": PipelineModel.parse_obj(pipeline_data).dict(by_alias=True), "evaluator": evaluator.persist(), "timeSeries": timeSeries})
        await update_model_status(id, project, ModelStatus.done)
    except Exception as e:
        print(e)
        print(traceback.format_exc())


async def train(trainReq, project, background_tasks):
    data = trainReq.dict(by_alias=True)
    model = Model(name = trainReq.name, trainRequest=data, projectId=project)
    id = await add_model(model=model.dict(by_alias=True))
    background_tasks.add_task(init_train, trainReq, id, project)
    return id