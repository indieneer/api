from flask import Blueprint, request, g, current_app

from app.middlewares import requires_auth
from config import app_config
from lib.http_utils import respond_error, respond_success

from app.models import get_models, exceptions as models_exceptions
from app.models.profiles import Profile, ProfileCreate

profiles_controller = Blueprint('profiles', __name__, url_prefix='/profiles')


@profiles_controller.route('/<string:profile_id>', methods=["GET"])
def get_profile(profile_id: str):
    """
    Retrieve a user profile by its ID.

    This endpoint fetches the details of a user profile from the database, identified by the profile_id.
    The function raises an exception if the profile is not found.

    :param str profile_id: The unique identifier of the profile to be retrieved.
    :raises NotFoundException: If the profile with the given ID does not exist.
    :return: The requested profile in JSON format.
    :rtype: dict
    """

    profile_model = get_models(current_app).profiles
    profile = profile_model.get(profile_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success(profile.to_json())


@profiles_controller.route('/', methods=["POST"])
def create_profile():
    """
    Create a new user profile.

    This endpoint is responsible for creating a new user profile.
    It expects a JSON payload containing the necessary profile information, specifically 'email' and 'password'.
    The function validates the incoming data and returns an error response if the validation fails.

    :return: The created profile in JSON format along with a status code indicating successful creation.
    :rtype: dict
    :status 201: Profile created successfully.
    """

    data = request.get_json()
    profile_model = get_models(current_app).profiles

    if data is None or not all(key in data and len(data[key]) > 0 for key in ('email', 'password', 'nickname')):
        return respond_error("Bad Request.", 400)

    profile_data = ProfileCreate(
        email=data.get("email"),
        password=data.get("password"),
        nickname=data.get("nickname"),
        email_verified=False
    )

    profile = profile_model.create(profile_data)

    return respond_success(profile.to_json(), None, 201)


@profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
def update_profile(profile_id: str):
    raise Exception("Not implemented")


@profiles_controller.route('/<string:profile_id>', methods=["DELETE"])
@requires_auth
def delete_profile(profile_id: str):
    """
    Delete a user's profile.

    The user profile is deleted based on the provided user ID.
    The operation is only allowed if the invoker's ID matches the provided user ID.

    :param str profile_id: The ID of the user whose profile is to be deleted.
    :raises ForbiddenException: If the invoker's ID does not match the user ID.
    :raises NotFoundException: If a profile with the provided user ID is not found.
    :return: A success response with acknowledgment if the profile is deleted successfully.
    :rtype: dict
    """
    invoker_id = g.get("payload").get(f'{app_config["FB_NAMESPACE"]}/profile_id')

    if invoker_id != profile_id:
        raise models_exceptions.ForbiddenException

    profiles = get_models(current_app).profiles
    profile = profiles.delete(profile_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success({"acknowledged": True})


@profiles_controller.route('/me', methods=["GET"])
@requires_auth
def get_authenticated_profile():
    """
    Retrieve the profile of the currently authenticated user.

    This endpoint requires authentication and returns the profile of the currently authenticated user.
    The function raises an exception if the profile is not found or if there is an issue with the authentication payload.

    :raises NotFoundException: If the profile is not found or the authentication payload is invalid.
    :return: A dictionary representing the user's profile.
    :rtype: dict
    """

    # Accessing the profile model and payload containing the profile ID from the global object
    profiles_model = get_models(current_app).profiles
    payload = g.get("payload")

    if payload is None:
        raise

    # Extracting the profile ID from the payload
    profile_id = g.get("payload").get(f'{app_config["FB_NAMESPACE"]}/profile_id')

    if profile_id is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    # Retrieving the profile associated with the ID
    profile = profiles_model.get(profile_id)

    if profile is None:
        raise models_exceptions.NotFoundException(Profile.__name__)

    return respond_success(profile.to_json())
