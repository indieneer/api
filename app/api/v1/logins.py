from auth0 import Auth0Error
from flask import Blueprint, request, current_app

from lib.http_utils import respond_success, respond_error
from app.models import get_models

logins_controller = Blueprint('logins', __name__, url_prefix='/logins')


@logins_controller.route('/', methods=["POST"])
def logins():
    """
    Authenticate a user and provide JWT token(s) via Auth0.

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
        tokens = logins_model.login(email, password)
    except Auth0Error as error:
        return respond_error(error.message, error.status_code)

    return respond_success(tokens)


@logins_controller.route('/m2m', methods=["POST"])
def logins_m2m():
    """
    Perform a machine-to-machine (M2M) login.

    This endpoint handles POST requests to facilitate M2M login using client credentials.
    It requires a client ID and client secret, validates them, and returns appropriate tokens.

    :raises: Auth0Error if authentication fails.
    :return: A dictionary containing the authentication tokens.
    :rtype: dict
    """
    logins_model = get_models(current_app).logins

    data = request.get_json()

    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    if not client_id or not client_secret:
        return respond_error("Client ID and client secret are required.", 400)

    try:
        tokens = logins_model.login_m2m(client_id, client_secret)
    except Auth0Error as error:
        return respond_error(error.message, error.status_code)

    return respond_success(tokens)
