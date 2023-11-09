# from app.Deploy.CPP.cPart import CPart
from app.ml.PipelineExport.C.Common.CPart import CStep
from jinja2 import FileSystemLoader, Template, Environment


templateLoader = FileSystemLoader(searchpath="app/Deploy/Sklearn/Templates")
templateEnv = Environment(loader=templateLoader)

def convert(clf):
    tree = {
        'left': clf.tree_.children_left,
        'right': clf.tree_.children_right,
        'features': clf.tree_.feature,
        'thresholds': clf.tree_.threshold,
        'classes': clf.tree_.value,
        'i': 0
    }

    functions = {"f": {
        "enumerate": enumerate,
        'round': lambda x: round(x, 12),
    }}

    

    data = {**functions}
    code = templateEnv.get_template("decisiontree.jinja").render(tree, **data)
    
    variables = {**tree, **functions}

    return CStep(variables, code, input_mem, output_mem)

    return CPart([], [], code, {**tree, **functions})