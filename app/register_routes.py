from flask import Flask

from .api.v1.router import v1_router
from .api.v2.router import v2_router


def register_routes(app: Flask):
    app.register_blueprint(v1_router)
    app.register_blueprint(v2_router)