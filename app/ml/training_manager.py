from pebble import ProcessPool
from concurrent.futures import TimeoutError
from typing import Dict, List

import asyncio
import time
from app.db.models import add_model
from app.db.models.model import Model

from app.ml.trainer import Trainer
from app.ml.training_state import TrainingState

class TrainingManager:
    pool: ProcessPool
    trainers: Dict[str, Trainer]

    def __init__(self) -> None:
        self.pool = ProcessPool()
        self.trainers = dict()

    def all(self) -> List[Trainer]:
        return self.trainers.values()

    def has(self, id: str) -> bool:
        return id in self.trainers

    def get(self, id: str) -> Trainer:
        assert self.has(id)
        return self.trainers[id]

    def destroy(self):
        self.pool.close()

    def handle_timeout(self, t: Trainer):
        t.training_state = TrainingState.TRAINING_FAILED
        t.error_msg = "Task took too long and cancelled!"
        time.sleep(60)
        del self.trainers[t.id]

    # TODO: implement caching for each intermeditary variable
    def start(self, t: Trainer):
        self.trainers[t.id] = t
        time_left = 35
        t.training_state = TrainingState.TRAINING_INITIATED
        
        print("PHASE 1 Begin")
        start = time.perf_counter()
        initiate_training = self.pool.schedule(t.get_df_labeled_each_dataset, timeout=time_left)
        try:
            labels, df_labeled_each_dataset = initiate_training.result()
        except TimeoutError:
            print("Task took too long in phase 1")
            self.handle_timeout(t)
            return
        time_left -= time.perf_counter() - start
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
        time_left -= time.perf_counter() - start
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
        time_left -= time.perf_counter() - start
        print('PHASE 3 End: ', time_left)

        # print(time.perf_counter() - start)
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


