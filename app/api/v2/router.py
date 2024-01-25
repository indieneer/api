from flask import Blueprint

from .profiles import profiles_controller
from .logins import logins_controller

v2_router = Blueprint('v2', __name__, url_prefix='/v2')

v2_router.register_blueprint(profiles_controller)
v2_router.register_blueprint(logins_controller)
