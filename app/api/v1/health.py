from flask import Blueprint, current_app
from pymongo.errors import ServerSelectionTimeoutError

from lib.http_utils import respond_success
from app.services import get_services
from config import app_config

health_controller = Blueprint('health', __name__, url_prefix='/health')


@health_controller.route('/')
def health():
    """
    Check the health status of the Indieneer API.

    This endpoint pings the database and retrieves the application environment and version.
    It's primarily used for monitoring the application's health.

    :return: A dictionary that contains the database info: status, environment, and version.
    :rtype: dict
    """

    health_obj = {
        "db": None,
        "env": app_config.get("ENVIRONMENT"),
        "version": app_config.get("VERSION")
    }

    try:
        db = get_services(current_app).db
        mongodb_status = db.connection.command("ping")
        health_obj["db"] = mongodb_status.get("ok", 0.0)
    except ServerSelectionTimeoutError as error:
        health_obj["db"] = str(error)

    return respond_success(health_obj)
