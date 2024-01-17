from os import environ as env

from flask import Flask
from flask_cors import CORS

from config import app_config


def configure_app(app: Flask):
    app.config.update(**app_config)

    app.secret_key = env.get("APP_SECRET_KEY")
    app.url_map.strict_slashes = False

    python_env = env.get("PYTHON_ENV")

    origin = "http://localhost:3000"
    if python_env == "staging":
        origin = "http://*.indieneer.com"
    elif python_env == "production":
        origin = "http://indieneer.com"

    CORS(app, resources={r"/v1/*": {"origins": origin}})
