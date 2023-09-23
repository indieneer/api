from auth0.authentication import GetToken
from flask import Blueprint, request
from os import environ as env

from tools.http_utils import respond_success

logins_controller = Blueprint('logins', __name__, url_prefix='/logins')


@logins_controller.route('/', methods=["POST"])
def logins():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    domain = env.get("AUTH0_DOMAIN")
    client_id = env.get("AUTH0_CLIENT_ID")
    client_secret = env.get("AUTH0_CLIENT_SECRET")

    token = GetToken(domain, client_id, client_secret=client_secret)

    response = token.login(username=email, password=password, realm='Username-Password-Authentication', scope="openid profile email address phone offline_access", grant_type="password", audience="https://api.indieneer.com")

    return respond_success(response)