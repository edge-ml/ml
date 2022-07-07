import m2cgen as m2c

from app.models.edge_model import EdgeModel

def export_javascript(model: EdgeModel):
    return 'exports.score = ' + m2c.export_to_javascript(model.clf)