from starlette.config import Config

config = Config(".env")

SECRET_KEY = config("SECRET_KEY")
API_URI = config("API_URI")
DATABASE_URI = config('DATABASE_URI')
DATABASE_NAME = config('DATABASE_NAME', default="ml_def_db_name")
AUTH_DATABASE_URI = config('AUTH_DATABASE_URI')
AUTH_DATABASE_NAME = config('AUTH_DATABASE_NAME', default="aura_dev")
DATASTORE_DB_NAME = config('DATASTORE_DB_NAME', default="dataset_store")
CLASSIFIER_STORE = config('CLASSIFIER_STORE')
TS_STORE_MECHANISM = config("TS_STORE_MECHANISM")
TSDATA = config("TSDATA")
S3_URL = config("S3_URL")
S3_BUCKET_NAME = config("S3_BUCKET_NAME")
S3_ACCESS_KEY = config("S3_ACCESS_KEY")
S3_SECRET_KEY = config("S3_SECRET_KEY")