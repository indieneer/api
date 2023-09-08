from dotenv import find_dotenv, load_dotenv
from os import environ as env

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

configuration = {
    "ENVIRONMENT": env.get("PYTHON_ENV"),
    "VERSION": "0.0.2",
    "AUTH0_DOMAIN": env.get("AUTH0_DOMAIN"),
    "AUTH0_AUDIENCE": env.get("AUTH0_AUDIENCE"),
    "MONGO_URI": env.get("MONGO_URI")
}
