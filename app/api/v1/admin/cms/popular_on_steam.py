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
    popular_on_steam_model = get_models(current_app).popular_on_steam
    popular_on_steam = popular_on_steam_model.get_all()

    if popular_on_steam is None:
        raise models_exceptions.NotFoundException(PopularOnSteam.__name__)

    return respond_success(popular_on_steam)


@popular_on_steam_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_popular_on_steam():
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
    except TypeError as e:
        print(str(e))
        raise exceptions.BadRequestException("Bad request.")


@popular_on_steam_controller.route('/<string:popular_on_steam_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_popular_on_steam(popular_on_steam_id):
    popular_on_steam_model = get_models(current_app).popular_on_steam
    result = popular_on_steam_model.delete(popular_on_steam_id)

    if result == 0:
        return respond_error(f'No popular on steam with id {popular_on_steam_id} found.', 404)

    return respond_success(f'Popular on steam with id {popular_on_steam_id} deleted.')
