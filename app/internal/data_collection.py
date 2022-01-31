import aiohttp

from app.internal.config import API_URI

async def fetch_project_datasets(project_id, token):
    url = API_URI + "/datasets/"
    headers={"Authorization": "Bearer " + token, "project": project_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as res:
            return [x["_id"] for x in await res.json()]


async def fetch_dataset(project_id, token, dataset_id):
    url = API_URI + "/datasets/" + dataset_id
    headers={"Authorization": "Bearer " + token, "project": project_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as dataset:
            return await dataset.json()
