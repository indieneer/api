from flask import Blueprint

from .popular_on_steam import popular_on_steam_controller

cms_controller = Blueprint('cms', __name__, url_prefix='/cms')

cms_controller.register_blueprint(popular_on_steam_controller)
