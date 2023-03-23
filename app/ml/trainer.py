import numpy as np


from app.DataModels.model import Model
from app.db.models import add_model, update_model_status, ModelStatus, set_model_data
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset


from app.DataProcessor.DataPreProcessor import getDatasetWindows, calculateFeatures
from app.DataProcessor.DataLoader.DataLoader import processDataset
from app.ml.Evaluation import get_eval_by_name
from app.DataModels.trainRequest import TrainRequest

from app.ml.Classifier import get_classifier_by_name
from app.ml.Normalizer import get_normalizer_by_name
from app.ml.Windowing import get_windower_by_name



# def trainClassifier(windows, labels, modelInfo):
#     clf = model_map[modelInfo.classifier]()
#     # clf.hyperparameters = modelInfo.hyperparameters
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf


async def init_train(trainReq : TrainRequest, id, project):
    print("init training")
    await update_model_status(id, project, ModelStatus.preprocessing)

    # Get the datasets and lableings used for training
    datasets = [await get_dataset(x.id, project) for x in trainReq.datasets]
    labeling = await get_labeling(trainReq.labeling, project)
    
    labelMap = {str(x.id): i for i, x in enumerate(labeling.labels)}

    print("datasets: ", len(datasets))

    arrs = []
    for dataset in datasets:
        arrs.append(processDataset(dataset, trainReq.labeling, labelMap))

    
    windower = get_windower_by_name(trainReq.windowing.name)(trainReq.windowing.parameters)
    print(len(arrs))
    windows, labels = windower.window(arrs)


    windows = calculateFeatures(windows)
    print(windows.shape)

    # TODO: Need to select the correct labels, based on user selection
    filter = np.array([x != 100000 for x in labels])
    print(filter.shape)
    train_x = windows[filter]
    train_y = labels[filter]

    print(list(train_y).count(1), list(train_y).count(2))


    await update_model_status(id, project, ModelStatus.fitting_model)
    clf = get_classifier_by_name(trainReq.classifier.name)(trainReq.classifier.parameters)
    normalizer = get_normalizer_by_name(trainReq.normalizer.name)(trainReq.normalizer.parameters)
    labels = [x.name for x in labeling.labels]
    evaluator = get_eval_by_name(trainReq.evaluation["name"])(train_x, train_y, clf, normalizer, labels, trainReq.evaluation["parameters"])
    evaluator.train_eval()
    model_config = evaluator.persist()
    await set_model_data(id, project, {"model": model_config})
    await update_model_status(id, project, ModelStatus.done)



async def train(trainReq, project, background_tasks):
    data = trainReq.dict(by_alias=True)
    model = Model(name = trainReq.name, trainRequest=data, projectId=project)
    id = await add_model(model=model.dict(by_alias=True))
    background_tasks.add_task(init_train, trainReq, id, project)
    return id