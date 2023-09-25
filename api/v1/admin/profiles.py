from bson import ObjectId
from flask import Blueprint, request
from pymongo import ReturnDocument

from middlewares import requires_auth, requires_role
from services.database import Database as dbs
from tools.http_utils import respond_success, respond_error

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')

# Should we create the models folder of something?
PROFILE_FIELDS = [
    "email",
    "password",
    "name",
    "nickname",
    "date_of_birth"
]


@profiles_controller.route('/<string:profile_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_profile(profile_id):
    try:
        filter_criteria = {"_id": ObjectId(profile_id)}

        profile = dbs.client.get_default_database()["profiles"].find_one(filter_criteria)

        if profile is None:
            return respond_error(f'The profile with id {profile_id} was not found.', 404)

        profile["_id"] = str(profile["_id"])

        return respond_success(profile)
    except Exception as e:
        print(e)
        return respond_error(str(e), 500)


@profiles_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_profiles():
    try:
        db = dbs.client.get_default_database()

        profiles = []
        for profile in db["profiles"].find():
            profile["_id"] = str(profile["_id"])
            profiles.append(profile)

        return respond_success(profiles)

    except Exception as e:
        return respond_error(str(e), 500)


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def change_profile(profile_id):
    try:
        data = request.get_json()

        if len(data) == 0:
            return respond_error(f'The request body is empty.', 422)

        for key in data:
            if key not in PROFILE_FIELDS:
                return respond_error(f'The key "{key}" is not allowed.', 422)

        filter_criteria = {"_id": ObjectId(profile_id)}

        profiles = dbs.client.get_default_database()["profiles"]

        result = profiles.find_one_and_update(filter_criteria, {"$set": data}, return_document=ReturnDocument.AFTER)
        if result is None:
            return respond_error(f'The profile with id {profile_id} was not found.', 404)

        result["_id"] = str(result["_id"])

        return respond_success(result)

    except Exception as e:
        return respond_error(str(e), 500)
