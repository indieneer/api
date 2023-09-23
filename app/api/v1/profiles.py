from bson import ObjectId
from flask import Blueprint, request, g, current_app

from pymongo import ReturnDocument
from pymongo.errors import ServerSelectionTimeoutError

from app.services import get_services
from config.constants import AUTH0_ROLES, Auth0Role
from app.middlewares import requires_auth
from lib.http_utils import respond_error, respond_success
from lib import db_utils

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')

# available fields for a profile object
PROFILE_FIELDS = [
    "email",
    "password",
    "name",
    "nickname",
    "date_of_birth"
]


@profiles_controller.route('/<string:profile_id>', methods=["GET"])
def get_profile(profile_id):
    try:
        filter_criteria = {"_id": ObjectId(profile_id)}

        db = get_services(current_app).db.connection
        profile = db["profiles"].find_one(filter_criteria)

        if profile is None:
            return respond_error(f'The profile with id {profile_id} was not found.', 404)

        profile["_id"] = str(profile["_id"])

        return respond_success(profile)
    except Exception as e:
        return respond_error(str(e), 500)


@profiles_controller.route('/', methods=["POST"])
def create_profile():
    services = get_services(current_app)
    db = services.db.connection
    auth0_mgmt = services.auth0.client

    profiles = db["profiles"]

    data = request.get_json()

    new_profile = {key: data.get(key) for key in PROFILE_FIELDS}

    email = new_profile["email"]
    password = new_profile["password"]

    user = auth0_mgmt.users.create({"email": email, "password": password, "email_verified": True,
                                    "connection": "Username-Password-Authentication"})

    idp_id = user["user_id"]
    auth0_mgmt.users.add_roles(idp_id, [AUTH0_ROLES[Auth0Role.User.value]])

    try:
        new_profile["idp_id"] = idp_id
        profiles.insert_one(new_profile)
    except ServerSelectionTimeoutError as e:
        return respond_error(str(e), 500)

    new_profile = db_utils.as_json(new_profile)

    auth0_mgmt.users.update(
        idp_id, {"user_metadata": {"profile_id": new_profile["_id"]}})

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

        db = get_services(current_app).db.connection
        filter_criteria = {"_id": ObjectId(profile_id)}

        result = db["profiles"].find_one_and_update(filter_criteria, {"$set": data},
                                                    return_document=ReturnDocument.AFTER)

        if result is None:
            return respond_error(f'The user with id {profile_id} was not found.', 404)

        return respond_success(db_utils.as_json(result))
    except Exception as e:
        return respond_error(str(e), 500)


@profiles_controller.route('/<string:user_id>', methods=["DELETE"])
@requires_auth
def delete_profile(user_id):
    invoker_id = g.get("payload").get('https://indieneer.com/profile_id')

    if not invoker_id == user_id:
        return respond_error("Forbidden", 403)

    try:
        services = get_services(current_app)
        db = services.db.connection
        auth0_mgmt = services.auth0.client

        auth0_mgmt.users.delete(g.get("payload").get('sub'))

        result = db["profiles"].find_one_and_delete({"_id": ObjectId(user_id)})

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
        db = get_services(current_app).db.connection
        profile = db["profiles"].find_one({"_id": ObjectId(profile_id)})

        if profile is None:
            return respond_error(f'The profile with id {profile_id} was not found.', 404)

        return respond_success(db_utils.as_json(profile))
    except Exception as e:
        return respond_error(str(e), 500)
