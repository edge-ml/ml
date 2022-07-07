import requests

from app.internal.config import API_URI

# TODO handle exceptions more informatively
def fetch_project_datasets(project_id, token):
    url = API_URI + "/datasets/"
    try:
        samples = requests.get(
            url, headers={"Authorization": "Bearer " + token, "project": project_id}
        )
    except:
        return []
    return [x["_id"] for x in samples.json()]


def fetch_dataset(project_id, token, dataset_id):
    url = API_URI + "/datasets/" + dataset_id
    try:
        dataset = requests.get(
            url, headers={"Authorization": "Bearer " + token, "project": project_id}
        )
    except:
        return []
    return dataset.json()

def fetch_label_definition(project_id, token):
    url = API_URI + "/labelDefinitions"
    label_definitions = requests.get(
        url, headers={"Authorization": "Bearer " + token, "project": project_id}
    )
    return label_definitions.json()
