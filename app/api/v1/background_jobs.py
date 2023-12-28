from flask import Blueprint, request, current_app, g

from app.middlewares import requires_auth, requires_service_account
from app.models import get_models, exceptions as models_exceptions
from app.models.background_jobs import BackgroundJob, BackgroundJobCreate, BackgroundJobPatch, EventCreate
from lib.http_utils import respond_success
from lib import db_utils
import app.api.exceptions as exceptions

background_jobs_controller = Blueprint(
    'background_jobs', __name__, url_prefix='/background_jobs')


@background_jobs_controller.route('/health', methods=["GET"])
@requires_auth
@requires_service_account
def health():
    return respond_success({
        "alive": True
    })


@background_jobs_controller.route('/<string:job_id>', methods=["GET"])
@requires_auth
@requires_service_account
def get_background_job(job_id: str):
    """
    Retrieve a background job by its ID.

    :param str job_id: The ID of the background job to retrieve.
    :return: The requested background job in JSON format.
    :raises NotFoundException: If the background job with the given ID does not exist.
    :raises ForbiddenException: If the background job was not created by the user.
    :rtype: dict
    """
    background_job = get_models(current_app).background_jobs.get(job_id)
    if background_job is None:
        raise models_exceptions.NotFoundException(BackgroundJob.__name__)
    if background_job.created_by != g.get("payload").get("sub"):
        raise models_exceptions.ForbiddenException()

    return respond_success(background_job.to_json())


@background_jobs_controller.route('/', methods=["GET"])
@requires_auth
@requires_service_account
def get_all_background_jobs():
    """
    Retrieve all background jobs.

    :return: The requested background jobs in JSON format.
    :rtype: dict
    """
    jobs = get_models(current_app).background_jobs.get_all()

    return respond_success(db_utils.to_json(jobs))


@background_jobs_controller.route('/', methods=["POST"])
@requires_auth
@requires_service_account
def create_background_job():
    """
    Create a new background job.

    :return: The created background job in JSON format.
    :raises BadRequestException: If the request body is not valid.
    :rtype: dict
    :status 201: Background job created successfully.
    """
    data = request.get_json()

    background_job_model = get_models(current_app).background_jobs
    if data is None or not all(key in data for key in ('type', 'metadata')):
        raise exceptions.BadRequestException("Not all required fields are present")

    try:
        background_job = background_job_model.create(
            BackgroundJobCreate(**data, created_by=g.get("payload").get("sub")))

        return respond_success(background_job.to_json(), status_code=201)
    except ValueError as e:
        raise exceptions.BadRequestException(str(e))


@background_jobs_controller.route('/<string:job_id>', methods=["PATCH"])
@requires_auth
@requires_service_account
def update_background_job(job_id: str):
    """
    Update a background job.

    :param str job_id: The ID of the background job to update.
    :return: The updated background job in JSON format.
    :raises BadRequestException: If the request body is not valid.
    :raises NotFoundException: If the background job with the given ID does not exist.
    :raises ForbiddenException: If the background job was not created by the user.
    :rtype: dict
    """
    data = request.get_json()
    if data is None or not any(key in data for key in ('status', 'metadata')):
        raise exceptions.BadRequestException("No valid fields are present")

    background_job_model = get_models(current_app).background_jobs

    background_job = get_models(current_app).background_jobs.get(job_id)
    if background_job is None:
        raise models_exceptions.NotFoundException(BackgroundJob.__name__)
    if background_job.created_by != g.get("payload").get("sub"):
        raise models_exceptions.ForbiddenException()

    try:
        background_job = background_job_model.patch(job_id, BackgroundJobPatch(**data))
        if background_job is None:
            raise models_exceptions.NotFoundException(BackgroundJob.__name__)

        return respond_success(background_job.to_json())
    except ValueError as e:
        raise exceptions.BadRequestException(str(e))
    except TypeError:
        raise exceptions.BadRequestException("Bad request.")


@background_jobs_controller.route('/<string:job_id>/events', methods=["POST"])
@requires_auth
@requires_service_account
def create_background_job_event(job_id: str):
    """
    Create a new background job event.

    :param str job_id: The ID of the background job to update.
    :return: The updated background job in JSON format.
    :raises BadRequestException: If the request body is not valid.
    :raises NotFoundException: If the background job with the given ID does not exist.
    :raises ForbiddenException: If the background job was not created by the user.
    :rtype: dict
    """
    data = request.get_json()

    if data is None or not all(key in data for key in ('type', 'message')):
        raise exceptions.BadRequestException("Not all required fields are present")

    background_job = get_models(current_app).background_jobs.get(job_id)
    if background_job is None:
        raise models_exceptions.NotFoundException(BackgroundJob.__name__)
    if background_job.created_by != g.get("payload").get("sub"):
        raise models_exceptions.ForbiddenException()

    try:
        background_job = get_models(current_app).background_jobs.add_event(job_id, EventCreate(**data))
        if background_job is None:
            raise models_exceptions.NotFoundException(BackgroundJob.__name__)

        return respond_success(background_job.to_json())
    except ValueError as e:
        raise exceptions.BadRequestException(str(e))
