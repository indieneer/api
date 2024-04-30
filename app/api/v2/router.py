from flask import Blueprint

from .search import search_controller

v2_router = Blueprint('v2', __name__, url_prefix='/v2')

v2_router.register_blueprint(search_controller)
