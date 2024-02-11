from bson import ObjectId
from flask import Blueprint, request, current_app
from pymongo import ReturnDocument

from app.middlewares import requires_auth, requires_role
from app.services import get_services
from lib.http_utils import respond_success, respond_error

service_profiles_controller = Blueprint(
    'service_profiles', __name__, url_prefix='/service_profiles')


@service_profiles_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_service_profiles():
    raise Exception("Not implemented")


@service_profiles_controller.route('/<string:profile_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_service_profile(profile_id: str):
    raise Exception("Not implemented")


@service_profiles_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_service_profile():
    raise Exception("Not implemented")


@service_profiles_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def patch_service_profile(profile_id: str):
    raise Exception("Not implemented")


@service_profiles_controller.route('/<string:profile_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_service_profile(profile_id: str):
    raise Exception("Not implemented")
