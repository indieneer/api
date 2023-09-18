from dotenv import find_dotenv, load_dotenv
from os import environ as env

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

configuration = {
    "ENVIRONMENT": env.get("PYTHON_ENV"),
    "PORT": env.get("PORT"),
    "VERSION": "0.0.2",
    "AUTH0_DOMAIN": env.get("AUTH0_DOMAIN"),
    "AUTH0_CLIENT_ID": env.get("AUTH0_CLIENT_ID"),
    "AUTH0_CLIENT_SECRET": env.get("AUTH0_CLIENT_SECRET"),
    "AUTH0_AUDIENCE": env.get("AUTH0_AUDIENCE"),
    "AUTH0_NAMESPACE": env.get("AUTH0_NAMESPACE"),
    "AUTH0_ROLES": env.get("AUTH0_ROLES"),
    "MONGO_URI": env.get("MONGO_URI"),
    "ROOT_USER_EMAIL": env.get("ROOT_USER_EMAIL"),
    "ROOT_USER_PASSWORD": env.get("ROOT_USER_PASSWORD")
}

# comprehension to create dict in format ROLE: ID
AUTH0_ROLES = {key: value for key, value in [x.split(':') for x in configuration["AUTH0_ROLES"].split(',')]}
