import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List

import time
from app.db.models import add_model
from app.db.models.model import Model

from app.ml.trainer import Trainer
from app.ml.training_state import TrainingState

from codecarbon import OfflineEmissionsTracker
import csv
import os

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
        if os.path.exists('emissions.csv'):
            os.remove('emissions.csv')
        emissions_tracker = OfflineEmissionsTracker(log_level = "CRITICAL", country_iso_code="DEU")
        emissions_tracker.start()

        self.trainers[t.id] = t

        t.training_state = TrainingState.TRAINING_INITIATED
        try:
            labels, df_labeled_each_dataset = await asyncio.get_running_loop().run_in_executor(self.executor, t.get_df_labeled_each_dataset)
            t.training_state = TrainingState.FEATURE_EXTRACTION
            data_x, data_y = await asyncio.get_running_loop().run_in_executor(self.executor, t.feature_extraction, df_labeled_each_dataset)
            t.training_state = TrainingState.MODEL_TRAINING
            model, metrics = await asyncio.get_running_loop().run_in_executor(self.executor, t.train, data_x, data_y)
            t.training_state = TrainingState.TRAINING_SUCCESSFUL
        except ValueError as err:
            t.training_state = TrainingState.TRAINING_FAILED
            t.error_msg = str(err)
            await asyncio.sleep(60)
            del self.trainers[t.id]
            return

        emissions_tracker.stop()
        with open('emissions.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            data = next(csv_reader)

            emissions = round(float(data[4]) * 1e6, 2) #in milligram
            energy = round(float(data[12]) * 36e5, 2) #in Joules

            print("Energy consumed for training (in Joule): ", energy)
            print("This resulted in the following emissions (in milligram CO₂): ", emissions)
        
        if os.path.exists('emissions.csv'):
            os.remove('emissions.csv')

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


