from os import environ as env

from flask import Flask

from config import app_config


def configure_app(app: Flask):
    app.config.update(**app_config)

    app.secret_key = env.get("APP_SECRET_KEY")
    app.url_map.strict_slashes = False
