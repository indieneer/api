from flask import Blueprint, request, current_app

from lib.http_utils import respond_success, respond_error
from app.models import get_models

logins_controller = Blueprint('logins', __name__, url_prefix='/logins')


@logins_controller.route('/', methods=["POST"])
def logins():
    """
    Authenticate a user and provide JWT token(s) via Firebase.

    This endpoint is used to authenticate the user by email and password, and if successful,
    returns the authentication token(s).

    :return: Authentication token(s) if successful, otherwise an error message and status code.
    :rtype: dict or tuple
    """
    logins_model = get_models(current_app).logins

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # Input validation
    if not email or not password:
        return respond_error("Email and password are required.", 400)

    try:
        identity = logins_model.login_v2(email, password)

        return respond_success(identity.to_json())
    except Exception as error:
        return respond_error(str(error), 500)
