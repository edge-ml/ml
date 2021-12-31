import requests

from requests.models import HTTPError

def fetch_project_datasets(project_id, token):
    url = "http://localhost:3001/api" + "/datasets/"
    # print(url)
    try:
        samples = requests.get(url, headers={"Authorization": "Bearer " + token, "project": project_id})
    except:
        raise HTTPError
    return [x['_id'] for x in samples.json()]

def fetch_dataset(project_id, token, dataset_id):
    url = "http://localhost:3001/api/datasets/" + dataset_id
    try:
        dataset = requests.get(url, headers={"Authorization": "Bearer " + token, "project": project_id})
    except:
        raise HTTPError
    return dataset.json()