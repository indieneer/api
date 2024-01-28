from flask import Blueprint, request, g, current_app

from app.middlewares import requires_auth
from lib.http_utils import respond_error, respond_success

from app.models import get_models, exceptions as models_exceptions
from app.models.profiles import Profile, ProfileCreateV2, ProfilePatch

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')

# Available fields for a profile object
PROFILE_FIELDS = [
    "email",
    "password",
    "name",
    "nickname",
    "date_of_birth"
]


@profiles_controller.route('/', methods=["POST"])
def create_profile():
    """
    Create a new profile.

    :return: The created profile in JSON format.
    :rtype: dict
    :status 201: Profile created successfully.
    """

    profile_model = get_models(current_app).profiles
    data = request.get_json()

    if data is None or not all(key in data and len(data[key]) > 0 for key in ('email', 'password', 'nickname')):
        return respond_error("Bad Request.", 400)

    profile_data = ProfileCreateV2(
        email=data.get("email"),
        password=data.get("password"),
        nickname=data.get("nickname"),
        email_verified=False
    )

    profile = profile_model.create_v2(profile_data)

    return respond_success(profile.to_json(), None, 201)


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
def update_profile(profile_id: str):
    raise Exception("Not implemented")


@profiles_controller.route('/<string:user_id>', methods=["DELETE"])
@requires_auth
def delete_profile(user_id: str):
    """
    Delete a user's profile.

    The user profile is deleted based on the provided user ID.
    The operation is only allowed if the invoker's ID matches the provided user ID.

    :param str user_id: The ID of the user whose profile is to be deleted.
    :raises ForbiddenException: If the invoker's ID does not match the user ID.
    :raises NotFoundException: If a profile with the provided user ID is not found.
    :return: A success response with acknowledgment if the profile is deleted successfully.
    :rtype: dict
    """
    invoker_id = g.get("payload").get('https://indieneer.com/profile_id')

    if invoker_id != user_id:
        raise models_exceptions.ForbiddenException

    profiles = get_models(current_app).profiles
    profile = profiles.delete_v2(user_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success({"acknowledged": True})
