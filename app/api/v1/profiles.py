from flask import Blueprint, request, g, current_app

from app.middlewares import requires_auth
from lib.http_utils import respond_error, respond_success

from app.services import get_services
from app.models import get_models, exceptions as models_exceptions
from app.models.profiles import Profile, ProfileCreate, ProfilePatch
from lib import db_utils

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')

# Available fields for a profile object
PROFILE_FIELDS = [
    "email",
    "password",
    "name",
    "nickname",
    "date_of_birth"
]


@profiles_controller.route('/<string:profile_id>', methods=["GET"])
def get_profile(profile_id: str):
    """
    Retrieve a profile by its ID.

    :param str profile_id: The ID of the profile to retrieve.
    :return: The requested profile in JSON format.
    :raises NotFoundException: If the profile with the given ID does not exist.
    :rtype: dict
    """

    profile_model = get_models(current_app).profiles
    profile = profile_model.get(profile_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success(profile.as_json())


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

    if data is None or not all(key in data for key in ('email', 'password')):
        return respond_error("Bad Request.", 400)

    profile_data = ProfileCreate(
        email=data.get("email"),
        password=data.get("password")
    )

    profile = profile_model.create(profile_data)

    return respond_success(profile.as_json(), None, 201)


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
def update_profile(profile_id: str):
    """
    Update a user profile.

    This endpoint allows for the partial update of a user profile. Only the owner of the
    profile is allowed to make updates.

    :param str profile_id: The ID of the profile to be updated.
    :raises NotFoundException: If the profile was not found.
    :return: The updated profile or an error message.
    :rtype: dict
    """

    invoker_id = g.get("payload").get('https://indieneer.com/profile_id')

    if invoker_id != profile_id:
        raise models_exceptions.ForbiddenException

    data = request.get_json()

    # Validate the request data
    if not data:
        raise

    for key in data:
        if key not in PROFILE_FIELDS:
            return respond_error(f'The key "{key}" is not allowed.', 422)

    profiles_model = get_models(current_app).profiles
    updated = profiles_model.patch(profile_id, ProfilePatch(**data))

    if updated is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success(updated.as_json())


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
    profile = profiles.delete(user_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success({"acknowledged": True})


@profiles_controller.route('/me', methods=["GET"])
@requires_auth
def get_authenticated_profile():
    """
    Retrieve the profile of a user that is currently authenticated.

    This endpoint requires authentication and returns the profile of the currently authenticated user.

    :raises: NotFoundException if the profile is not found.
    :return: A dictionary representing the user's profile.
    :rtype: dict
    """

    # Accessing the profile model and payload containing the profile ID from the global object
    profiles_model = get_models(current_app).profiles
    payload = g.get("payload")

    if payload is None:
        raise

    # Extracting the profile ID from the payload
    profile_id = payload.get('https://indieneer.com/profile_id')

    if profile_id is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    # Retrieving the profile associated with the ID
    profile = profiles_model.get(profile_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success(profile.as_json())
