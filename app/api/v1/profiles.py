from bson import ObjectId
from flask import Blueprint, request, g, current_app

from pymongo import ReturnDocument

from app.middlewares import requires_auth
from lib.http_utils import respond_error, respond_success

from app.services import get_services
from app.models import get_models, exceptions
from app.models.profiles import Profile, ProfileCreate
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
    profiles = get_models(current_app).profiles

    profile = profiles.get(profile_id)

    if profile is None:
        raise exceptions.NotFoundException(Profile.__name__)

    return respond_success(profile.as_json())


@profiles_controller.route('/', methods=["POST"])
def create_profile():
    profiles = get_models(current_app).profiles
    data = request.get_json()

    input = ProfileCreate(
        email=data.get("email"),
        password=data.get("password")
    )

    profile = profiles.create(input)

    return respond_success(profile.as_json(), None, 201)


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
def update_profile(profile_id):
    # todo: rework
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

    profiles = get_models(current_app).profiles

    profile = profiles.delete(user_id)

    if profile is None:
        raise exceptions.NotFoundException(Profile.__name__)

    return respond_success({"acknowledged": True})


@profiles_controller.route('/me', methods=["GET"])
@requires_auth
def get_authenticated_profile():
    profiles = get_models(current_app).profiles

    profile_id = g.get("payload").get('https://indieneer.com/profile_id')

    profile = profiles.get(profile_id)

    if profile is None:
        raise exceptions.NotFoundException(Profile.__name__)

    return respond_success(profile.as_json())
