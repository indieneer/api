from flask import Blueprint, request, current_app

from app.middlewares import requires_auth, requires_role
from app.models.operating_systems import OperatingSystemCreate, OperatingSystemPatch
from app.models import get_models
from app.api import exceptions as handlers_exceptions
from lib.http_utils import respond_success, respond_error

operating_systems_controller = Blueprint(
    'operating-systems', __name__, url_prefix='/operating-systems')

OPERATING_SYSTEM_FIELDS = [
    "name"
]


@operating_systems_controller.route('/', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_operating_systems():
    """
    Retrieve a list of all operating systems.

    This endpoint fetches all operating system records from the database.
    It requires authentication and admin role permission for access.

    :return: A list of dictionaries, each representing the details of an operating system.
    :rtype: Response
    """

    operating_systems_model = get_models(current_app).operating_systems
    operating_systems = [os.as_json() for os in operating_systems_model.get_all()]

    return respond_success(operating_systems)


@operating_systems_controller.route('/<string:operating_system_id>', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_operating_system_by_id(operating_system_id: str):
    """
    Retrieve a specific operating system entry by its ID.

    This endpoint fetches details of a particular operating system from the database,
    identified by the operating_system_id. It requires authentication and admin role permission for access.

    :param str operating_system_id: The unique identifier of the operating system to be retrieved.
    :return: A dictionary containing the details of the requested operating system.
    :rtype: Response
    """

    operating_systems_model = get_models(current_app).operating_systems
    operating_system = operating_systems_model.get(operating_system_id)

    if not operating_system:
        return respond_error(f'The operating system with ID {operating_system_id} was not found.', 404)

    return respond_success(operating_system.as_json())


@operating_systems_controller.route('/', methods=["POST"])
@requires_auth
@requires_role("admin")
def create_operating_system():
    """
    Create a new operating system entry.

    This endpoint facilitates the addition of a new operating system record to the database.
    It requires admin authorization and expects a JSON payload with necessary operating system details.

    :raises BadRequestException: If the provided data is invalid or incomplete.
    :return: A dictionary containing the details of the newly created operating system.
    :rtype: Response
    """

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in OPERATING_SYSTEM_FIELDS):
        raise handlers_exceptions.BadRequestException("Invalid data provided.")

    new_os = {key: data[key] for key in OPERATING_SYSTEM_FIELDS}

    operating_systems_model = get_models(current_app).operating_systems
    created_operating_system = operating_systems_model.create(OperatingSystemCreate(**new_os))

    return respond_success(created_operating_system.as_json(), None, 201)


@operating_systems_controller.route('/<string:operating_system_id>', methods=["PATCH"])
@requires_auth
@requires_role("admin")
def update_operating_system(operating_system_id: str):
    """
    Update an existing operating system entry.

    This endpoint allows for the modification of an existing operating system record identified by the operating_system_id.
    Requires admin privileges and a JSON payload with the updated details of the operating system.

    :param str operating_system_id: The unique identifier of the operating system to be updated.
    :raises InternalServerErrorException: If no data is provided in the request.
    :raises UnprocessableEntityException: If the provided data contains keys not allowed in OPERATING_SYSTEM_FIELDS.
    :return: A dictionary representing the updated details of the operating system.
    :rtype: Response
    """

    data = request.get_json()

    if not data:
        raise handlers_exceptions.InternalServerErrorException("Internal server error.")

    for key in data:
        if key not in OPERATING_SYSTEM_FIELDS:
            raise handlers_exceptions.UnprocessableEntityException(f'The key "{key}" is not allowed.')

    operating_systems_model = get_models(current_app).operating_systems
    result = operating_systems_model.patch(operating_system_id, OperatingSystemPatch(**data))

    return respond_success(result.as_json())


@operating_systems_controller.route('/<string:operating_system_id>', methods=["DELETE"])
@requires_auth
@requires_role("admin")
def delete_operating_system(operating_system_id: str):
    """
    Delete an operating system entry.

    This endpoint removes an existing operating system record from the database using the provided operating_system_id.
    Access is restricted to users with admin roles.

    :param str operating_system_id: The unique identifier of the operating system to be deleted.
    :raises NotFoundException: If no operating system is found with the given operating_system_id.
    :return: A success message confirming the deletion along with the details of the deleted operating system.
    :rtype: Response
    """

    operating_systems_model = get_models(current_app).operating_systems
    deleted_operating_system = operating_systems_model.delete(operating_system_id)

    if deleted_operating_system is None:
        return respond_error(f'The operating system with ID {operating_system_id} was not found.', 404)

    return respond_success({"message": f"Operating system id {operating_system_id} successfully deleted", "deleted_os": deleted_operating_system.as_json()})
