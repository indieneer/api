from auth0.authentication import GetToken
from auth0.management import Auth0
from bson import ObjectId
from flask import Blueprint, request, _request_ctx_stack, g
from os import environ as env

from pymongo import ReturnDocument
from pymongo.errors import ServerSelectionTimeoutError

from services.database import Database as dbs
from tools.http_utils import respond_error, respond_success
from middlewares import requires_auth

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')

# available fields for a profile object
PROFILE_FIELDS = [
    "email",
    "password",
    "name",
    "nickname",
    "date_of_birth"
]

USER_ROLE_ID = 'rol_S6powqdVXBR9jmDI'  # maybe we should put such constants in a specific file?


@profiles_controller.route('/<string:profile_id>', methods=["GET"])
def get_profile(profile_id):
    try:
        filter_criteria = {"_id": ObjectId(profile_id)}

        profile = dbs.client.get_default_database()["profiles"].find_one(filter_criteria)

        if profile is None:
            return respond_error(f'The profile with id {profile_id} was not found.', 404)

        profile["_id"] = str(profile["_id"])

        return respond_success(profile)
    except Exception as e:
        return respond_error(str(e), 500)


@profiles_controller.route('/', methods=["POST"])
def create_profile():
    db = dbs.client.get_default_database()
    profiles = db["profiles"]

    data = request.get_json()

    new_profile = {key: data.get(key) for key in PROFILE_FIELDS}

    email = new_profile["email"]
    password = new_profile["password"]

    domain = env.get("AUTH0_DOMAIN")
    client_id = env.get("AUTH0_CLIENT_ID")
    client_secret = env.get("AUTH0_CLIENT_SECRET")

    get_token = GetToken(domain, client_id, client_secret=client_secret)
    token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
    mgmt_api_token = token['access_token']

    auth0 = Auth0(domain, mgmt_api_token)

    user = auth0.users.create({"email": email, "password": password, "email_verified": True,
                               "connection": "Username-Password-Authentication"})

    idp_id = user["identities"][0]["user_id"]
    auth0.users.add_roles("auth0|" + idp_id, [USER_ROLE_ID])

    try:
        new_profile["idp_id"] = idp_id
        profiles.insert_one(new_profile)
    except ServerSelectionTimeoutError as e:
        return respond_error(str(e), 500)

    new_profile["_id"] = str(new_profile["_id"])  # I hate this line

    auth0.users.update(f'auth0|{idp_id}', {"user_metadata": {"profile_id": new_profile["_id"]}})

    return respond_success(new_profile, None, 201)


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
def update_profile(profile_id):
    invoker_id = g.get("payload").get('https://indieneer.com/profile_id')

    if not invoker_id == profile_id:
        return respond_error("Forbidden", 403)

    try:
        data = request.get_json()

        for key in data:
            if key not in PROFILE_FIELDS:
                return respond_error(f'The key "{key}" is not allowed.', 422)

        filter_criteria = {"_id": ObjectId(profile_id)}

        result = dbs.client.indieneer.profiles.find_one_and_update(filter_criteria, {"$set": data},
                                                                   return_document=ReturnDocument.AFTER)

        if result is None:
            return respond_error(f'The user with id {profile_id} was not found.', 404)

        result["_id"] = str(result["_id"])

        return respond_success(result)
    except Exception as e:
        return respond_error(str(e), 500)


@profiles_controller.route('/<string:user_id>', methods=["DELETE"])
@requires_auth
def delete_profile(user_id):
    invoker_id = g.get("payload").get('https://indieneer.com/profile_id')

    if not invoker_id == user_id:
        return respond_error("Forbidden", 403)

    try:
        filter_criteria = {"_id": ObjectId(user_id)}

        domain = env.get("AUTH0_DOMAIN")
        client_id = env.get("AUTH0_CLIENT_ID")
        client_secret = env.get("AUTH0_CLIENT_SECRET")

        get_token = GetToken(domain, client_id, client_secret=client_secret)
        token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
        mgmt_api_token = token['access_token']

        auth0 = Auth0(domain, mgmt_api_token)

        auth0.users.delete(g.get("payload").get('sub'))

        result = dbs.client.indieneer.profiles.find_one_and_delete(filter_criteria)

        if result is None:
            return respond_error(f'The profile with id {user_id} was not found.', 404)

        return respond_success([f'Successfully deleted the profile with id {result["_id"]}.'])
    except Exception as e:
        return respond_error(str(e), 500)


@profiles_controller.route('/me', methods=["GET"])
@requires_auth
def get_authenticated_profile():
    profile_id = g.get("payload").get('https://indieneer.com/profile_id')

    try:
        filter_criteria = {"_id": ObjectId(profile_id)}

        profile = dbs.client.indieneer.profiles.find_one(filter_criteria)

        if profile is None:
            return respond_error(f'The profile with id {profile_id} was not found.', 404)

        profile["_id"] = str(profile["_id"])

        return respond_success(profile)
    except Exception as e:
        return respond_error(str(e), 500)
