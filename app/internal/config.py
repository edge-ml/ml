from starlette.config import Config

config = Config(".env")

SECRET_KEY = config("SECRET_KEY")
API_URI = config("API_URI")
DATABASE_URI = config('DATABASE_URI')
DATABASE_NAME = config('DATABASE_NAME', default="ml_def_db_name")
AUTH_DATABASE_URI = config('AUTH_DATABASE_URI')
AUTH_DATABASE_NAME = config('AUTH_DATABASE_NAME', default="aura_dev")