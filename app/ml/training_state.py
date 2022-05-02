from enum import Enum


class TrainingState(str, Enum):
    # Default state
    NO_TRAINING_YET = "NO_TRAINING_YET",
    # In progress training states
    TRAINING_INITIATED = "TRAINING_INITIATED"
    FEATURE_EXTRACTION = "FEATURE_EXTRACTION",
    MODEL_TRAINING = "MODEL_TRAINING",
    # Successful state
    TRAINING_SUCCESSFUL = "TRAINING_SUCCESSFUL"
    # Failure state
    TRAINING_FAILED = "TRAINING_FAILED"

    def is_in_progress_training_state(self):
        return self in _in_progress_training_states


_in_progress_training_states = [TrainingState.TRAINING_INITIATED,
                    TrainingState.FEATURE_EXTRACTION,
                    TrainingState.MODEL_TRAINING]