from flask import Blueprint

from .platforms import platforms_controller
from .platforms_os import platforms_os_controller
from .profiles import profiles_controller
from .products import products_controller
from .tags import tags_controller

admin_controller = Blueprint('admin', __name__, url_prefix='/admin')

admin_controller.register_blueprint(platforms_controller)
admin_controller.register_blueprint(platforms_os_controller)
admin_controller.register_blueprint(profiles_controller)
admin_controller.register_blueprint(products_controller)
admin_controller.register_blueprint(tags_controller)
