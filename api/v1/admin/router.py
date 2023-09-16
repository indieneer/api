from flask import Blueprint

from api.v1.admin.platforms import platforms_controller

admin_controller = Blueprint('admin', __name__, url_prefix='/admin')

admin_controller.register_blueprint(platforms_controller)
