from flask import Blueprint

from api.v1.admin.router import admin_controller
from api.v1.profiles import profiles_controller
from api.v1.products import products_controller
from api.v1.logins import logins_controller
from api.v1.health import health_controller

v1_router = Blueprint('v1', __name__, url_prefix='/v1')

v1_router.register_blueprint(profiles_controller)
v1_router.register_blueprint(products_controller)
v1_router.register_blueprint(logins_controller)
v1_router.register_blueprint(health_controller)

v1_router.register_blueprint(admin_controller)
