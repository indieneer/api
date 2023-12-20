from flask import Blueprint, request, current_app

from app.middlewares import requires_auth, requires_role
from app.models.platforms_os import PlatformOSCreate, PlatformOSPatch
from app.models import get_models
from app.api import exceptions as handlers_exceptions
from lib.http_utils import respond_success, respond_error

platforms_os_controller = Blueprint(
    'platforms-os', __name__, url_prefix='/platforms-os')

PLATFORM_OS_FIELDS = [
    "name"
]


@platforms_os_controller.route('/', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_platforms_os():
    """
    Retrieve a list of all platform operating systems.

    This endpoint fetches all operating system records associated with game platforms from the database.
    It requires authentication and admin role permission for access.

    :return: A list of dictionaries, each representing the details of an operating system for a gaming platform.
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms_os
    platforms = [platform.as_json() for platform in platforms_model.get_all()]

    return respond_success(platforms)


@platforms_os_controller.route('/<string:platform_os_id>', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_platform_os_by_id(platform_os_id: str):
    """
    Retrieve a specific operating system entry for a game platform by its ID.

    This endpoint fetches details of a particular operating system associated with game platforms from the database,
    identified by the platform_os_id. It requires authentication and admin role permission for access.

    :param str platform_os_id: The unique identifier of the operating system to be retrieved.
    :return: A dictionary containing the details of the requested operating system for a gaming platform.
    :rtype: Response
    """

    platforms_os_model = get_models(current_app).platforms_os
    platform_os = platforms_os_model.get(platform_os_id)

    if not platform_os:
        return respond_error(f'The platform with ID {platform_os_id} was not found.', 404)

    return respond_success(platform_os.as_json())


@platforms_os_controller.route('/', methods=["POST"])
@requires_auth
@requires_role("admin")
def create_platform_os():
    """
    Create a new operating system entry for a game platform.

    This endpoint facilitates the addition of a new operating system record to the game platforms in the database.
    It requires admin authorization and expects a JSON payload with necessary operating system details.

    :raises BadRequestException: If the provided data is invalid or incomplete.
    :return: A dictionary containing the details of the newly created operating system for a gaming platform.
    :rtype: Response
    """

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in PLATFORM_OS_FIELDS):
        raise handlers_exceptions.BadRequestException("Invalid data provided.")

    new_platform = {key: data[key] for key in PLATFORM_OS_FIELDS}

    platforms_os_model = get_models(current_app).platforms_os
    created_platform_os = platforms_os_model.create(PlatformOSCreate(**new_platform))

    return respond_success(created_platform_os.as_json(), None, 201)


@platforms_os_controller.route('/<string:platform_os_id>', methods=["PATCH"])
@requires_auth
@requires_role("admin")
def update_platform_os(platform_os_id: str):
    """
    Update an existing operating system entry for a game platform.

    This endpoint allows for the modification of an existing operating system record identified by the platform_os_id.
    Requires admin privileges and a JSON payload with the updated details of the operating system.

    :param str platform_os_id: The unique identifier of the operating system to be updated.
    :raises InternalServerErrorException: If no data is provided in the request.
    :raises UnprocessableEntityException: If the provided data contains keys not allowed in PLATFORM_OS_FIELDS.
    :return: A dictionary representing the updated details of the operating system.
    :rtype: Response
    """

    data = request.get_json()

    if not data:
        raise handlers_exceptions.InternalServerErrorException("Internal server error.")

    for key in data:
        if key not in PLATFORM_OS_FIELDS:
            raise handlers_exceptions.UnprocessableEntityException(f'The key "{key}" is not allowed.')

    platforms_os_model = get_models(current_app).platforms_os
    result = platforms_os_model.patch(platform_os_id, PlatformOSPatch(**data))

    return respond_success(result.as_json())


@platforms_os_controller.route('/<string:platform_os_id>', methods=["DELETE"])
@requires_auth
@requires_role("admin")
def delete_platform_os(platform_os_id: str):
    """
    Delete an operating system entry for a game platform.

    This endpoint removes an existing operating system record from the game platforms database using the provided platform_os_id.
    Access is restricted to users with admin roles.

    :param str platform_os_id: The unique identifier of the operating system to be deleted.
    :raises NotFoundException: If no operating system is found with the given platform_os_id.
    :return: A success message confirming the deletion along with the details of the deleted operating system.
    :rtype: Response
    """

    platforms_os_model = get_models(current_app).platforms_os
    deleted_platform_os = platforms_os_model.delete(platform_os_id)

    return respond_success({"message": f"Platform id {platform_os_id} successfully deleted", "deleted_platform": deleted_platform_os.as_json()})
