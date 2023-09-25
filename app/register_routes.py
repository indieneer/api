from flask import Flask

from .api.v1.router import v1_router


def register_routes(app: Flask):
    app.register_blueprint(v1_router)
