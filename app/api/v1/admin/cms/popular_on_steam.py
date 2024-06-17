import dataclasses

from flask import Blueprint, current_app, request

from app.api import exceptions
from app.middlewares import requires_auth, requires_role
from app.models import exceptions as models_exceptions
from app.models import get_models
from app.models.cms.popular_on_steam import PopularOnSteam, PopularOnSteamCreate, PopularOnSteamPatch
from lib.http_utils import respond_success, respond_error

popular_on_steam_controller = Blueprint('popular_on_steam', __name__, url_prefix='/popular_on_steam')


@popular_on_steam_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_popular_on_steam():
    """
    Retrieve all popular games on Steam.

    This endpoint is accessible only to authenticated users with the 'admin' role. It fetches all entries
    from the popular_on_steam model. If no entries are found, a NotFoundException is raised.

    :raises NotFoundException: If no popular games are found in the popular_on_steam model.
    :return: A success response containing the list of popular games on Steam.
    :rtype: Response
    """
    popular_on_steam_model = get_models(current_app).popular_on_steam
    popular_on_steam = popular_on_steam_model.get_all()

    if popular_on_steam is None:
        raise models_exceptions.NotFoundException(PopularOnSteam.__name__)

    return respond_success(popular_on_steam)


@popular_on_steam_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_popular_on_steam():
    """
    Create a new entry in the popular_on_steam model.

    This endpoint is accessible only to authenticated users with the 'admin' role. It expects a JSON
    payload with all required fields to create a new popular game entry. If the data is invalid or
    missing required fields, a BadRequestException is raised.

    :raises BadRequestException: If the request data is missing required fields or is invalid.
    :return: A success response containing the created popular game entry.
    :rtype: Response
    """
    data = request.get_json()

    popular_on_steam_model = get_models(current_app).popular_on_steam
    popular_on_steam_create_fields = [field.name for field in dataclasses.fields(PopularOnSteamCreate)]
    if data is None or not all(key in data for key in popular_on_steam_create_fields):
        raise exceptions.BadRequestException("Not all required fields are present.")

    try:
        created_popular_on_steam = popular_on_steam_model.create(PopularOnSteamCreate(**data))

        return respond_success(created_popular_on_steam.to_json(), status_code=201)
    except TypeError:
        raise exceptions.BadRequestException("Bad request.")


@popular_on_steam_controller.route('/<string:popular_on_steam_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_popular_on_steam(popular_on_steam_id):
    """
    Update an existing entry in the popular_on_steam model.

    This endpoint is accessible only to authenticated users with the 'admin' role. It expects a JSON
    payload with the fields to be updated for the specified popular game entry. If the data is invalid
    or contains fields that are not allowed, a BadRequestException or a 422 error is raised. If the
    entry is not found, a NotFoundException is raised.

    :param popular_on_steam_id: The ID of the popular game entry to update.
    :type popular_on_steam_id: str
    :raises BadRequestException: If the request data is empty or invalid.
    :raises NotFoundException: If the specified popular game entry is not found.
    :return: A success response containing the updated popular game entry.
    :rtype: Response
    """
    data = request.get_json()

    popular_on_steam_model = get_models(current_app).popular_on_steam
    product_update_fields = [field.name for field in dataclasses.fields(PopularOnSteamPatch)]
    if data is None:
        raise exceptions.BadRequestException("The request body is empty.")
    for key in data:
        if key not in product_update_fields:
            return respond_error(f'The key "{key}" is not allowed.', 422)

    try:
        updated_popular_on_steam = popular_on_steam_model.patch(popular_on_steam_id, PopularOnSteamPatch(**data))
        if updated_popular_on_steam is None:
            raise models_exceptions.NotFoundException(PopularOnSteam.__name__)

        return respond_success(updated_popular_on_steam.to_json())
    except TypeError:
        raise exceptions.BadRequestException("Bad request.")


@popular_on_steam_controller.route('/<string:popular_on_steam_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_popular_on_steam(popular_on_steam_id):
    """
    Delete an existing entry in the popular_on_steam model.

    This endpoint is accessible only to authenticated users with the 'admin' role. It deletes the specified
    popular game entry by its ID. If no entry is found with the given ID, a 404 error is returned.

    :param popular_on_steam_id: The ID of the popular game entry to delete.
    :type popular_on_steam_id: str
    :return: A success response indicating the popular game entry has been deleted, or an error response
             if no entry is found with the specified ID.
    :rtype: Response
    """
    popular_on_steam_model = get_models(current_app).popular_on_steam
    result = popular_on_steam_model.delete(popular_on_steam_id)

    if result == 0:
        return respond_error(f'No popular on steam with id {popular_on_steam_id} found.', 404)

    return respond_success(f'Popular on steam with id {popular_on_steam_id} deleted.')
