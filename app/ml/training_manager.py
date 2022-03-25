import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Dict

import time
from app.db.models import add_model
from app.db.models.model import Model

from app.ml.trainer import Trainer

class TrainingManager:
    executor: ProcessPoolExecutor

    trainers: Dict[str, Trainer]

    def __init__(self) -> None:
        self.executor = ProcessPoolExecutor()
        self.trainers = dict()
        pass

    def add(self, t: Trainer) -> str:
        self.trainers[t.id] = t
        return t.id

    def has(self, id: str) -> bool:
        return id in self.trainers

    def get(self, id: str) -> Trainer:
        assert self.has(id)
        return self.trainers[id]

    def destroy(self):
        self.executor.shutdown()
        pass

    @staticmethod
    def train(t: Trainer):
        (labels, df_labeled_each_dataset) = t.get_df_labeled_each_dataset()
        data_x, data_y = t.feature_extraction(df_labeled_each_dataset)
        model, metrics = t.train(data_x, data_y)

        return model, metrics, labels

    # TODO: implement caching for each intermeditary variable
    async def start(self, id: str):
        t = self.get(id)
        model, metrics, labels = await asyncio.get_running_loop().run_in_executor(self.executor, TrainingManager.train, t)

        id = await add_model(Model(
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
            confusion_matrix=metrics['confusion_matrix'],
            classification_report=metrics['classification_report'],
            edge_model=model
        ))
        print('id', id)
        # TODO(discussion): should we do anything with the model now? link it up with training etc maybe?


