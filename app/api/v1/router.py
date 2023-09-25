from flask import Blueprint

from .admin.router import admin_controller
from .platforms import platforms_controller
from .profiles import profiles_controller
from .logins import logins_controller
from .health import health_controller
from .search import search_controller

v1_router = Blueprint('v1', __name__, url_prefix='/v1')

v1_router.register_blueprint(profiles_controller)
v1_router.register_blueprint(logins_controller)
v1_router.register_blueprint(health_controller)
v1_router.register_blueprint(platforms_controller)
v1_router.register_blueprint(search_controller)

v1_router.register_blueprint(admin_controller)
