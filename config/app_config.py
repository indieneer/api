from .environment import setup_environment
from os import environ as env

setup_environment()

app_config = {
    "VERSION": env.get("VERSION", "0.0.1"),
    "ENVIRONMENT": env.get("PYTHON_ENV", "development"),
    "PORT": env.get("PORT", 5001),
    "AUTH0_DOMAIN": env.get("AUTH0_DOMAIN", ""),
    "AUTH0_CLIENT_ID": env.get("AUTH0_CLIENT_ID", ""),
    "AUTH0_CLIENT_SECRET": env.get("AUTH0_CLIENT_SECRET", ""),
    "AUTH0_AUDIENCE": env.get("AUTH0_AUDIENCE", ""),
    "AUTH0_NAMESPACE": env.get("AUTH0_NAMESPACE", ""),
    "AUTH0_ROLES": env.get("AUTH0_ROLES", ""),
    "MONGO_URI": env.get("MONGO_URI", ""),
    "ROOT_USER_EMAIL": env.get("ROOT_USER_EMAIL", ""),
    "ROOT_USER_PASSWORD": env.get("ROOT_USER_PASSWORD", "")
}