from pebble import ProcessPool
from concurrent.futures import TimeoutError
from typing import Dict, List

import asyncio
import time
from app.db.models import add_model
from app.db.models.model import Model
from app.ml.subscription_level import SubscriptionLevel

from app.ml.trainer import Trainer
from app.ml.training_state import TrainingState

from app.internal.data_collection import fetch_dataset, fetch_project_datasets
from app.internal.data_preparation import filter_by_timeseries, format_hyperparameters

class TrainingManager:
    pool: ProcessPool
    trainers: Dict[str, Trainer]

    def __init__(self) -> None:
        self.pool = ProcessPool()
        self.trainers = dict()

    def all(self, project_id: str) -> List[Trainer]:
        return filter(lambda t: t.project_id == project_id, self.trainers.values())

    def has(self, id: str, project_id: str) -> bool:
        return (id in self.trainers and self.trainers[id].project_id == project_id)

    def get(self, id: str, project_id: str) -> Trainer:
        if not self.has(id, project_id):
            raise KeyError("Trainer with id doesn't exist")
        return self.trainers[id]

    def destroy(self):
        self.pool.close()

    def handle_error(self, t: Trainer, error_msg: str):
        t.training_state = TrainingState.TRAINING_FAILED
        t.error_msg = error_msg
        time.sleep(60)
        del self.trainers[t.id]

    def handle_timeout(self, t: Trainer):
        self.handle_error(t, "Task took too long and cancelled!")

    @staticmethod
    def _calculate_time_left(time_left: float, time_passed: float):
        if time_left is not None:
            return time_left - time_passed
        return None

    def initiate(
                self, token, 
                model_name, project_id, 
                target_labeling, labels, selected_timeseries,
                window_size, sliding_step, 
                use_unlabelled, unlabelled_name, 
                selected_model, raw_hyperparams, 
                sub_level):
        
        t = Trainer(
            model_name, project_id, 
            target_labeling, labels, selected_timeseries, 
            window_size, sliding_step, 
            use_unlabelled, unlabelled_name, 
            selected_model, 
            sub_level)

        self.trainers[t.id] = t
        t.training_state = TrainingState.TRAINING_INITIATED
        dataset_ids = fetch_project_datasets(project_id, token)
        if not dataset_ids:
            self.handle_error("No dataset is available")
        
        datasets = [fetch_dataset(project_id, token, id) for id in dataset_ids]
        if any(hasattr(d, "error") for d in datasets):
            self.handle_error("Requested dataset cannot be found in the project")

        hyperparameters = format_hyperparameters(raw_hyperparams)
        filtered_datasets = filter_by_timeseries(datasets, selected_timeseries)
        
        t.hyperparameters = hyperparameters
        t.datasets = filtered_datasets
        
        self.start(t)

    # TODO: implement caching for each intermeditary variable
    def start(self, t: Trainer):
        time_left = SubscriptionLevel.corresponding_timer(t.sub_level)
        
        print("PHASE 1 Begin")
        start = time.perf_counter()
        initiate_training = self.pool.schedule(t.get_df_labeled_each_dataset, timeout=time_left)
        try:
            labels, df_labeled_each_dataset = initiate_training.result()
        except TimeoutError:
            print("Task took too long in phase 1")
            self.handle_timeout(t)
            return
        end = time.perf_counter()
        time_left = self._calculate_time_left(time_left, end - start)
        print('PHASE 1 End: ', time_left)
        
        print("PHASE 2")
        start = time.perf_counter()
        t.training_state = TrainingState.FEATURE_EXTRACTION
        feature_extraction = self.pool.schedule(t.feature_extraction, args=[df_labeled_each_dataset], timeout=time_left)
        try:
            data_x, data_y = feature_extraction.result()
        except TimeoutError:
            print("Task took too long in phase 2")
            self.handle_timeout(t)
            return
        end = time.perf_counter()
        time_left = self._calculate_time_left(time_left, end - start)
        print('PHASE 2 End: ', time_left)

        print("PHASE 3")
        start = time.perf_counter()
        t.training_state = TrainingState.MODEL_TRAINING
        training = self.pool.schedule(t.train, args=[data_x, data_y], timeout=time_left)
        try:
            model, metrics = training.result()
        except TimeoutError:
            print("Task took too long in phase 3")
            self.handle_timeout(t)
            return
        end = time.perf_counter()
        time_left = self._calculate_time_left(time_left, end - start)
        print('PHASE 3 End: ', time_left)

        t.training_state = TrainingState.TRAINING_SUCCESSFUL
        
        asyncio.run(add_model(Model(
            name=t.name,
            id=None,
            project_id=t.project_id,
            creation_date=time.time(),
            accuracy_score=metrics['accuracy_score'],
            precision_score=metrics['precision_score'],
            f1_score=metrics['f1_score'],
            recall_score=metrics['recall_score'],
            labels=list(labels),
            timeseries=t.selected_timeseries,
            window_size=t.window_size,
            sliding_step=t.sliding_step,
            confusion_matrix=metrics['confusion_matrix'],
            classification_report=metrics['classification_report'],
            edge_model=model
        )))
        del self.trainers[t.id]


