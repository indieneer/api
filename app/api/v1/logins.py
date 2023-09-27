from auth0.authentication import GetToken
from flask import Blueprint, request, current_app

from config import app_config
from lib.http_utils import respond_success
from app.models import get_models

logins_controller = Blueprint('logins', __name__, url_prefix='/logins')


@logins_controller.route('/', methods=["POST"])
def logins():
    logins = get_models(current_app).logins

    data = request.get_json()

    email = data["email"]
    password = data["password"]

    tokens = logins.login(email, password)

    return respond_success(tokens)
