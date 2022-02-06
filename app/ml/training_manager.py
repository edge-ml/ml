from asyncio import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor
from typing import Dict

import time
from app.db.models import add_model
from app.db.models.model import Model

from app.ml.trainer import Trainer

class TrainingManager:
    executor: ProcessPoolExecutor
    loop: AbstractEventLoop

    trainers: Dict[str, Trainer]

    def __init__(self, loop) -> None:
        self.executor = ProcessPoolExecutor()
        self.loop = loop
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

    # TODO: implement caching for each intermeditary variable
    async def start(self, id: str):
        t = self.get(id)
        df_labeled_each_dataset = await self.loop.run_in_executor(self.executor, t.get_df_labeled_each_dataset)
        data_x, data_y = await self.loop.run_in_executor(self.executor, t.feature_extraction, df_labeled_each_dataset)
        (model, metrics) = await self.loop.run_in_executor(self.executor, t.train, data_x, data_y)

        id = await add_model(Model(
            name="TODO IMPLEMENT", # we need names... for the models we create
            id=None,
            project_id=t.project_id,
            creation_date=time.time(),
            accuracy_score=metrics['accuracy_score'],
            precision_score=metrics['precision_score'],
            f1_score=metrics['f1_score'],
            recall_score=metrics['recall_score'],
            confusion_matrix=metrics['confusion_matrix'],
            classification_report=metrics['classification_report'],
            edge_model=model
        ))
        print('id', id)
        # TODO(discussion): should we do anything with the model now? link it up with training etc maybe?


