
from app.models.edge_model import EdgeModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from jinja2 import FileSystemLoader, Environment


templateLoader = FileSystemLoader("app/mcuConverter/templates")
templateEnv = Environment(loader=templateLoader,
                          trim_blocks=True, lstrip_blocks=True)

def convertMCU(model: EdgeModel, window_size, labels, timeseries, scaler):
    print("scaler: ", scaler)
    params = {"window_size": window_size,
        "num_sensors": len(timeseries),
        "num_classes": len(labels),
        "num_features": 10, # This is hardcoded for now
        "timeSeries": timeseries,
        "labels": labels,
        "scaler": scaler}

    functions = {"f": {
        "enumerate": enumerate,
        'round': lambda x: round(x, 12),
    }}
    clf = model.clf
    if isinstance(clf, RandomForestClassifier):
        trees = [{
            'left': clf.tree_.children_left,
            'right': clf.tree_.children_right,
            'features': clf.tree_.feature,
            'thresholds': clf.tree_.threshold,
            'classes': clf.tree_.value,
        } for clf in clf.estimators_]
        data = {**functions, **params, "trees": trees}
        template = templateEnv.get_template("randomforest/randomforest.jinja")
        interface = template.render(data=data)
    
    elif isinstance(clf, DecisionTreeClassifier):
        tree = {
            'left': clf.tree_.children_left,
            'right': clf.tree_.children_right,
            'features': clf.tree_.feature,
            'thresholds': clf.tree_.threshold,
            'classes': clf.tree_.value,
            'i': 0
        
        }
        data = {**functions, **params}
        template = templateEnv.get_template("decisiontree/decisiontree.jinja")
        interface = template.render(data=data, **tree)

    else:
        raise NotImplementedError("SVM is not implemented for conversion")

        '''
    if isinstance(clf, SVC):
        

        support_v = clf.support_vectors_
        n_classes = len(clf.n_support_)

        svm = {'kernel': {
            'type': clf.kernel,
            'gamma': clf.gamma,
            'coef0': clf.coef0,
            'degree': clf.degree
        },
        'sizes': {
            'features': len(support_v[0]),
            'vectors': len(support_v),
            'classes': n_classes,
            'decisions': n_classes * (n_classes - 1) // 2,
            'supports': clf.n_support_
        },
        'arrays': {
            'supports': support_v,
            'intercepts': clf.intercept_,
            'coefs': clf.dual_coef_
        }}
        data = {**functions, **params}
        template = templateEnv.get_template("svm/svm.jinja")
        interface = template.render(data=data, **svm)
        '''


    return interface