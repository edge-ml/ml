# ml
[![Publish Docker image](https://github.com/edge-ml/ml/actions/workflows/publishDocker.yaml/badge.svg)](https://github.com/edge-ml/ml/actions/workflows/publishDocker.yaml)

Machine learning component belonging to edge-ml.

Depends on fastapi and uvicorn.

Before you can run the server run:
```
pip3 install -r requirements.txt
```

(if you're using macOS and this fails, try [this](https://github.com/edge-ml/edge-ml/wiki#Troubleshooting))

Then create a .env file containing the credentials:

```
echo "SECRET_KEY=default_secret\nAPI_URI="http://localhost:3001/api"\nDATABASE_URI="mongodb://localhost:27017/aura_dev"\nAUTH_DATABASE_URI="mongodb://localhost:27017/aura_dev"\nAUTH_DATABASE_NAME="aura_dev"" > .env
```

(The credentials are as follows)
```
SECRET_KEY=default_secret
API_URI="http://localhost:3001/api"
DATABASE_URI="mongodb://localhost:27017/aura_dev"
AUTH_DATABASE_URI="mongodb://localhost:27017/aura_dev"
AUTH_DATABASE_NAME="aura_dev"
```

Run the server using 
```
python3 main.py
```
