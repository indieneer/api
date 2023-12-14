from flask import Blueprint, request, current_app

from app.models import get_models
from app.models.background_jobs import BackgroundJobCreate, BackgroundJobPatch, EventCreate
from lib.http_utils import respond_success, respond_error

background_jobs_controller = Blueprint(
    'background_jobs', __name__, url_prefix='/background_jobs')


@background_jobs_controller.route('/health', methods=["GET"])
def health():
    return respond_success({
        "alive": True
    })


@background_jobs_controller.route('/<string:job_id>', methods=["GET"])
def get_background_job(job_id: str):
    """
    Retrieve a background job by its ID.

    :param str job_id: The ID of the background job to retrieve.
    :return: The requested background job in JSON format.
    :rtype: dict
    """
    background_job = get_models(current_app).background_jobs.get(job_id)

    if background_job is None:
        return respond_error("not found", 404)

    return respond_success(background_job.as_json())


@background_jobs_controller.route('/', methods=["GET"])
def get_background_jobs():
    """
    Retrieve all background jobs.

    :return: The requested background jobs in JSON format.
    :rtype: dict
    """
    return respond_success(get_models(current_app).background_jobs.get_all())


@background_jobs_controller.route('/', methods=["POST"])
def create_background_job():
    """
    Create a new background job.

    :return: The created background job in JSON format.
    :rtype: dict
    :status 201: Background job created successfully.
    """
    data = request.get_json()

    background_job_model = get_models(current_app).background_jobs
    if data is None or not all(key in data for key in ('type', 'metadata')):
        return respond_error("Bad request.", 400)

    background_job = background_job_model.create(BackgroundJobCreate(**data, created_by="admin"))

    return respond_success(background_job.to_json(), status_code=201)


@background_jobs_controller.route('/<string:job_id>', methods=["PATCH"])
def update_background_job(job_id: str):
    """
    Update a background job.

    :param str job_id: The ID of the background job to update.
    :return: The updated background job in JSON format.
    :rtype: dict
    """
    data = request.get_json()
    if data is None or not any(key in data for key in ('status', 'metadata')):
        return respond_error("bad request", 400)

    background_job_model = get_models(current_app).background_jobs

    try:
        background_job = background_job_model.patch(job_id, BackgroundJobPatch(**data))
        if background_job is None:
            return respond_error("background job not found", 404)

        return respond_success(background_job.to_json())
    except ValueError or TypeError as e:
        return respond_error(str(e), 400)


@background_jobs_controller.route('/<string:job_id>/events', methods=["POST"])
def create_background_job_event(job_id: str):
    """
    Create a new background job event.

    :param str job_id: The ID of the background job to update.
    :return: The updated background job in JSON format.
    :rtype: dict
    """
    data = request.get_json()
    try:
        background_job = get_models(current_app).background_jobs.create_and_append_event(job_id, EventCreate(**data))
        if background_job is None:
            return respond_error("not found", 404)

        return respond_success(background_job.to_json())
    except ValueError as e:
        return respond_error(str(e), 400)
