from auth0.authentication import GetToken
from flask import Blueprint, request

from config import app_config
from lib.http_utils import respond_success

logins_controller = Blueprint('logins', __name__, url_prefix='/logins')


@logins_controller.route('/', methods=["POST"])
def logins():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    domain = app_config["AUTH0_DOMAIN"]
    client_id = app_config["AUTH0_CLIENT_ID"]
    client_secret = app_config["AUTH0_CLIENT_SECRET"]
    audience = app_config["AUTH0_AUDIENCE"]

    token = GetToken(domain, client_id, client_secret=client_secret)

    response = token.login(
        username=email,
        password=password,
        realm='Username-Password-Authentication',
        scope="openid profile email address phone offline_access",
        grant_type="password",
        audience=audience
    )

    return respond_success(response)
