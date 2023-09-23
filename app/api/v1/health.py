from flask import Blueprint, current_app
from pymongo.errors import ServerSelectionTimeoutError

from lib.http_utils import respond_success, respond_error
from app.services import get_services

health_controller = Blueprint('health', __name__, url_prefix='/health')


@health_controller.route('/')
def health():
    try:
        db = get_services(current_app).db

        mongodb_status = db.connection.command("ping")
        health_obj = {
            "db": mongodb_status,
            "env": current_app.config.get("ENVIRONMENT"),
            "version": current_app.config.get("VERSION")
        }
        return respond_success(health_obj)
    except ServerSelectionTimeoutError as e:
        health_obj = {
            "db": str(e),
            "env": current_app.config.get("ENVIRONMENT"),
            "version": current_app.config.get("VERSION")
        }
        return respond_success(health_obj)
    except Exception as e:
        return respond_error(str(e), 500)
