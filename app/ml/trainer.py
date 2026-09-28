

from app.DataModels.model import Model, ModelStatus
from app.db.models import ModelDB
from app.db.labelings import get_labeling
from app.db.datasets import get_dataset
from app.DataProcessor.DataLoader.DataLoader import processDatasets
from app.DataModels.PipelineRequest import PipelineStep, PipelineStepOption

from app.DataModels.model import Labeling


from app.ml.Pipelines.Categories.Evaluation import get_eval_by_name
from app.DataModels.trainRequest import TrainRequest

from app.ml.Pipeline import Pipeline
from app.DataModels.PipeLine import PipelineModel
from app.DataModels import PipelineRequest
from app.ml.Pipelines.PipelineContainer import PipelineContainer
import traceback

from app.ml.fit_to_pipeline import fit_to_pipeline, buildPipeline, getEvaluator
from app.ml.PipelineExport.formats import computeFormats


modelDB = ModelDB()


# def trainClassifier(windows, labels, modelInfo):
#     clf = model_map[modelInfo.classifier]()
#     # clf.hyperparameters = modelInfo.hyperparameters
#     windows = np.reshape(windows, (windows.shape[0], np.multiply(*windows.shape[1:])))
#     clf.fit(windows, labels)
#     return clf




async def init_train(trainReq : PipelineRequest, model : Model, id, project):
    try:
        model.trainStatus = ModelStatus.training
        model.stage = "Loading data"
        modelDB.update_model(id, project, model)
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


        # pipeline, evaluator = fit_to_pipeline(trainReq, datasets_processed, datasetMetaData, labels)

        pipeline : Pipeline = buildPipeline(trainReq)
        evaluator = getEvaluator(trainReq)

        data = PipelineContainer(datasets_processed, None, datasetMetaData)

        # Live training progress. Coarse "Training" stage for every classifier;
        # classifiers with an epoch loop (the Torch ones) additionally report
        # per-epoch progress via the callback below. State lives in Mongo (the
        # frontend polls the model doc), since training runs in a background task
        # and the poll may be served by a different worker process.
        model.stage = "Training"
        model.currentEpoch = None
        model.totalEpochs = None
        model.progress = None
        modelDB.update_model(id, project, model)

        _last = {"pct": -1}

        def report_epoch(current, total):
            pct = int(current / total * 100) if total else 0
            # Throttle writes to one per whole percent, but always emit the last epoch.
            if pct == _last["pct"] and current != total:
                return
            _last["pct"] = pct
            model.stage = "Training"
            model.currentEpoch = current
            model.totalEpochs = total
            model.progress = pct
            modelDB.update_model(id, project, model)

        for opt in pipeline.options:
            opt.progress_cb = report_epoch

        performance = pipeline.eval(data, labels)

        # Post-training work (persist, format detection, ExecuTorch precompile)
        # can take a moment; show a finishing stage and clear the epoch counters.
        model.stage = "Finalizing"
        model.currentEpoch = None
        model.totalEpochs = None
        model.progress = None
        modelDB.update_model(id, project, model)

        timeSeries = [x.name for x in datasets[0].timeSeries]


        for i, cs in enumerate(pipeline.persist()):
            model.pipeline.selectedPipeline.steps[i].options = cs


        model.timeSeries = timeSeries
        model.samplingRate = samplingRate
        model.formats = computeFormats(pipeline.options)

        # Precompile and cache the ExecuTorch .pte now, so downloads only stream
        # bytes instead of re-running the (expensive) tracing/lowering per click.
        # A compile failure just drops EXECUTORCH from the advertised formats
        # rather than failing the whole training run.
        if "EXECUTORCH" in (model.formats or []):
            try:
                from app.ml.PipelineExport.Executorch.ExecutorchCompiler import (
                    buildExecutorchPte,
                    storeExecutorchPte,
                )
                storeExecutorchPte(model, buildExecutorchPte(pipeline.options, model))
            except Exception as e:
                print("ExecuTorch precompile failed; removing EXECUTORCH from formats:", e)
                print(traceback.format_exc())
                model.formats = [f for f in model.formats if f != "EXECUTORCH"]

        # Validate the PyTorch (TorchScript) export the same way: only advertise
        # it if the trace actually succeeds for this architecture, so the UI never
        # offers a download that would fail. Cheap (a trace), so just verify here.
        if "PYTORCH" in (model.formats or []):
            try:
                from app.ml.PipelineExport.PyTorch.PyTorchCompiler import buildPytorchExport
                buildPytorchExport(pipeline.options, model)
            except Exception as e:
                print("PyTorch export unavailable; removing PYTORCH from formats:", e)
                print(traceback.format_exc())
                model.formats = [f for f in model.formats if f != "PYTORCH"]

        model.labels = [x.dict(by_alias=True) for x in selectedLabels] + ([{"name": "Zero", "color": "#ffffff"}] if trainReq.labeling.useZeroClass else [])

        model.labels = [Labeling(**x) for x in model.labels]

        print(model.labels)

        model.trainStatus = ModelStatus.done
        model.stage = None
        model.progress = 100

        modelDB.update_model(id, project, model)
    except Exception as e:
        print("Train_error!")
        print(e)
        print(traceback.format_exc())
        model.error = str(e)
        model.trainStatus = ModelStatus.error
        modelDB.update_model(id, project, model)
        raise e


async def train(req: PipelineRequest, project, background_tasks):
    try:
        data = req.dict(by_alias=True)
        model = Model(name=req.name, pipeline=req, projectId=project)
        id = modelDB.add_model(model)
        background_tasks.add_task(init_train, req, model, id, project)
        return id
    except Exception as e:
        print("Train_error!")
        print(e)
        print(traceback.format_exc())
        raise e