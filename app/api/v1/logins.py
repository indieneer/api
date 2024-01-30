
from flask import Blueprint, request, current_app

from lib.http_utils import respond_success, respond_error
from app.models import get_models

logins_controller = Blueprint('logins', __name__, url_prefix='/logins')
