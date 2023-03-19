import numpy as np


from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset
from time import sleep

from app.models.random_forest import RandomForest

from app.DataProcessor.DataPreProcessor import getDatasetWindows, extract_features, calculateFeatures
from app.DataProcessor.DataLoader.DataLoader import processDataset
from app.ml.Evaluation import get_eval_by_name
from app.DataModels.trainRequest import TrainRequest

from app.ml.Classifier import get_classifier_by_name
from app.ml.Normalizer import get_normalizer_by_name



# def trainClassifier(windows, labels, modelInfo):
#     clf = model_map[modelInfo.classifier]()
#     # clf.hyperparameters = modelInfo.hyperparameters
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf


async def init_train(trainReq : TrainRequest, id, project):
    await update_model_status(id, project, ModelStatus.preprocessing)

    # Get the datasets and lableings used for training
    datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
    labeling = await get_labeling(trainReq.labeling, project)
    
    labelMap = {str(x.id): i+1 for i, x in enumerate(labeling.labels)}

    all_windows = []
    all_labels = []
    for dataset in datasets:
        arr = processDataset(dataset, trainReq.labeling, labelMap)
        windows, labels = getDatasetWindows(arr, window_size=50, stride=20)
        windows = calculateFeatures(windows)
        print(windows.shape)
        all_windows.append(windows)
        all_labels.extend(labels)

    all_windows = np.concatenate(all_windows, axis=0)
    all_labels = np.array(all_labels)

    # TODO: Need to select the correct labels, based on user selection
    filter = np.array([x > 0 for x in all_labels])
    train_x = all_windows[filter]
    train_y = all_labels[filter]

    await update_model_status(id, project, ModelStatus.fitting_model)
    clf = get_classifier_by_name(trainReq.modelInfo.classifier)(trainReq.modelInfo.hyperparameters)
    normalizer = get_normalizer_by_name(trainReq.normalizer.name)(trainReq.normalizer.parameters)
    evaluator = get_eval_by_name(trainReq.evaluation["name"])(train_x, train_y, clf, normalizer, trainReq.evaluation["parameters"])
    evaluator.train_eval()
    



    return clf

async def train(trainReq, project, background_tasks):
    data = trainReq.dict(by_alias=True)
    storedHyperparameters = [{"name": str(x["name"]), "value": str(x["value"])} for x in trainReq.modelInfo.hyperparameters]
    model = Model(name = trainReq.name, hyperparameters=storedHyperparameters, classifier=trainReq.modelInfo.classifier, labeling=trainReq.labeling, datasets=data["datasets"], projectId=project)
    id = await add_model(model=model.dict(by_alias=True))
    background_tasks.add_task(init_train, trainReq, id, project)
    return id