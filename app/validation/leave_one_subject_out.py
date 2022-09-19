from .base_validation import BaseCrossValidation
from sklearn.model_selection import LeaveOneGroupOut, cross_validate

class LeaveOneSubjectOut(BaseCrossValidation):
    _name = 'LOSO'
    loso_variable: str

    def cross_validate(self, model, data, target, metadatas):
        logo = LeaveOneGroupOut()

        filtered = [ 'none' if d.get(self.loso_variable, None) is None else 'present-' + d[self.loso_variable] for d in metadatas ]
        print(len(data), len(target), len(metadatas))

        cross_dict = cross_validate(model.clf, data, target, cv=logo, groups=filtered, scoring=[
            'accuracy',
            'precision_weighted',
            'recall_weighted',
            'f1_weighted',
        ])

        # for details on the selection of scoring methods, see trainer.py#_calculate_model_metrics, we use the same ones as there
        return {
            'method': self._name,
            'loso_variable': self.loso_variable,
            'results': {k: v.tolist() for k, v in cross_dict.items()}
        }