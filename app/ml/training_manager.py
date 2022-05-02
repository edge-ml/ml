import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List

import time
from app.db.models import add_model
from app.db.models.model import Model

from app.ml.trainer import Trainer
from app.ml.training_state import TrainingState

class TrainingManager:
    executor: ProcessPoolExecutor

    trainers: Dict[str, Trainer]

    def __init__(self) -> None:
        self.executor = ProcessPoolExecutor()
        self.trainers = dict()

    def all(self) -> List[Trainer]:
        return self.trainers.values()

    def has(self, id: str) -> bool:
        return id in self.trainers

    def get(self, id: str) -> Trainer:
        assert self.has(id)
        return self.trainers[id]

    def destroy(self):
        self.executor.shutdown()

    # TODO: implement caching for each intermeditary variable
    async def start(self, t: Trainer):
        self.trainers[t.id] = t

        t.training_state = TrainingState.TRAINING_INITIATED
        try:
            labels, df_labeled_each_dataset = await asyncio.get_running_loop().run_in_executor(self.executor, t.get_df_labeled_each_dataset)
            t.training_state = TrainingState.FEATURE_EXTRACTION
            data_x, data_y = await asyncio.get_running_loop().run_in_executor(self.executor, t.feature_extraction, df_labeled_each_dataset)
            t.training_state = TrainingState.MODEL_TRAINING
            model, metrics = await asyncio.get_running_loop().run_in_executor(self.executor, t.train, data_x, data_y)
            t.training_state = TrainingState.TRAINING_SUCCESSFUL
        except ValueError:
            t.training_state = TrainingState.TRAINING_FAILED
            await asyncio.sleep(60)
            del self.trainers[t.id]
            return

        await add_model(Model(
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
        ))
        
        del self.trainers[t.id]


