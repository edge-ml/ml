from numpy import array2string
from sklearn.metrics import ( 
    accuracy_score, 
    confusion_matrix, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report
)

import json
from app.utils.jsonEncoder import JSONEncoder




# def calculateMetrics(y_test, y_pred):
#     print(y_test.shape)
#     print(y_pred.shape)
#     metrics = {}
#     metrics['accuracy_score'] = accuracy_score(y_test, y_pred)
#     metrics['precision_score'] = precision_score(y_test, y_pred, average='weighted')
#     metrics['recall_score'] = recall_score(y_test, y_pred, average='weighted')
#     metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted')
#     # num_labels = [float(idx) for idx, label in enumerate(self.labels)]
#     # target_names = self.labels
#     # if self.use_unlabelled:
#     #     num_labels.append(float(len(num_labels)))
#     #     target_names.append(self.unlabelled_name)
#     # metrics['confusion_matrix'] = array2string(confusion_matrix(y_test, y_pred, labels=num_labels))
#     # metrics['classification_report'] = classification_report(y_test, y_pred, labels=num_labels, zero_division=0, target_names=None)
#     return metrics


def calculateMetrics(y_test, y_pred, target_labels):
    metrics = {}
    print(list(zip(y_test, y_pred)))

    metrics['accuracy_score'] = accuracy_score(y_test, y_pred)
    metrics['precision_score'] = precision_score(y_test, y_pred, average='weighted')
    metrics['recall_score'] = recall_score(y_test, y_pred, average='weighted')
    metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted')
    num_labels = [float(idx) for idx, label in enumerate(target_labels)]
    # if self.use_unlabelled:
    if False:
        num_labels.append(float(len(num_labels)))
        target_labels.append(self.unlabelled_name)
    metrics['confusion_matrix'] = json.dumps(confusion_matrix(y_test, y_pred, labels=num_labels), cls=JSONEncoder)
    metrics['classification_report'] = classification_report(y_test, y_pred, labels=num_labels, zero_division=0, target_names=target_labels, output_dict=True)
    return metrics