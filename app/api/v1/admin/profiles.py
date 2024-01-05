from bson import ObjectId
from flask import Blueprint, request, current_app
from pymongo import ReturnDocument

from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.profiles import ProfilePatch
from lib import db_utils
from lib.http_utils import respond_success, respond_error

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')

# Should we create the models folder of something?
PROFILE_FIELDS = [
    "email",
    "password",
    "name",
    "nickname",
    "date_of_birth"
]


@profiles_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_profiles():
    """
    Fetch all profiles from the database.

    This function requires admin privileges. It retrieves all the profiles stored in the database.

    :return: A JSON response containing either all profiles or an error message.
    :rtype: dict
    """

    profiles = get_models(current_app).profiles.get_all()

    return respond_success(db_utils.to_json(profiles))


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def change_profile(profile_id):
    """
    Update a profile by its ID.

    This function requires admin privileges. The provided profile_id is used to update the specific profile's
    data in the database with the new data provided in the request's JSON body.

    :param str profile_id: The ID of the profile to be updated.
    :return: A JSON response containing either the updated profile data or an error message.
    :rtype: Response
    """
    data = request.get_json()

    if len(data) == 0:
        return respond_error(f'The request body is empty.', 422)

    for key in data:
        if key not in PROFILE_FIELDS:
            return respond_error(f'The key "{key}" is not allowed.', 422)

    profile_model = get_models(current_app).profiles

    profile = profile_model.get(profile_id)
    if profile is None:
        return respond_error(f'The profile with id {profile_id} was not found.', 404)

    profile = profile_model.patch(profile_id, ProfilePatch(**data))

    return respond_success(profile.to_json())
