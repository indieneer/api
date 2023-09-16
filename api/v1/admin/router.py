from flask import Blueprint

from api.v1.admin.platforms import platforms_controller
from api.v1.admin.products import products_controller

admin_controller = Blueprint('admin', __name__, url_prefix='/admin')

admin_controller.register_blueprint(platforms_controller)
admin_controller.register_blueprint(products_controller)
