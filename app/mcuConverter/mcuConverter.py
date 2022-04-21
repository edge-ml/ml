
from app.models.edge_model import EdgeModel
from jinja2 import FileSystemLoader, Environment


templateLoader = FileSystemLoader("app/mcuConverter/templates")
templateEnv = Environment(loader=templateLoader,
                          trim_blocks=True, lstrip_blocks=True)


def convertRandomForest(model: EdgeModel, window_size, labels, timeseries):
    clf = model.clf
    params = {"window_size": window_size,
              "num_sensors": len(timeseries),
              "num_classes": len(labels),
              "num_features": 10, # This is hardcoded for now
              "timeSeries": timeseries,
              "labels": labels}

    trees = [{
        'left': clf.tree_.children_left,
        'right': clf.tree_.children_right,
        'features': clf.tree_.feature,
        'thresholds': clf.tree_.threshold,
        'classes': clf.tree_.value,
    } for clf in clf.estimators_]

    functions = {"f": {
        "enumerate": enumerate
    }}

    data = {
        **functions,
        **params,
        "trees": trees
    }

    template = templateEnv.get_template("randomforest.jinja")
    interface = template.render(data=data)
    return interface
