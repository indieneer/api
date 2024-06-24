from flask import Blueprint, current_app, request, make_response
from werkzeug.exceptions import UnsupportedMediaType

from app.models import get_models
from app.services.firebase.exceptions import InvalidLoginCredentialsException
from lib.http_utils import respond_error, respond_success

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
        identity = logins_model.login(email, password)

        return respond_success(identity.to_json())
    except InvalidLoginCredentialsException as error:
        return respond_error('Wrong email or password.', 403)
    except Exception as error:
        return respond_error(str(error), 500)


@logins_controller.route('/m2m', methods=["POST"])
def logins_m2m():
    """
    Authenticate a user and provide JWT token(s) via Firebase.

    This endpoint is used to authenticate the user by email and password, and if successful,
    returns the authentication token(s).

    :return: Authentication token(s) if successful, otherwise an error message and status code.
    :rtype: dict or tuple
    """
    logins_model = get_models(current_app).logins

    data = request.get_json()

    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    # Input validation
    if not client_id or not client_secret:
        return respond_error("Client id and client secret are required.", 400)

    try:
        token = logins_model.login_m2m(client_id, client_secret)
        if token is None:
            return respond_error("Client id or client secret is incorrect", 401)

        return respond_success(token.to_json())
    except Exception as error:
        return respond_error(str(error), 500)


@logins_controller.route('/refresh_tokens', methods=["POST"])
def exchange_refresh_token():
    """
    Authenticate a user and provide JWT token(s) via Firebase.

    This endpoint is used to authenticate the user by email and password, and if successful,
    returns the authentication token(s).

    :return: Authentication token(s) if successful, otherwise an error message and status code.
    :rtype: dict or tuple
    """
    logins_model = get_models(current_app).logins

    try:
        data = request.get_json()
        refresh_token = data.get("refresh_token")
    except UnsupportedMediaType:
        refresh_token = request.cookies.get("RefreshToken")

    if not refresh_token:
        return respond_error("Refresh token is missing.", 400)

    try:
        identity = logins_model.exchange_refresh_token(refresh_token)
        response = make_response(respond_success(identity.to_json()))
        response.set_cookie("Authorization", identity.id_token, httponly=True, secure=True)
        response.set_cookie("RefreshToken", identity.refresh_token, httponly=True, secure=True)
        return response
    except Exception as error:
        return respond_error(str(error), 500)
