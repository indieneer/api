from flask import Blueprint, request, current_app

from app.models import get_models
from app.models.background_jobs import BackgroundJobCreate, BaseMetadata
from app.services import get_services
from lib.http_utils import respond_success, respond_error

background_jobs_controller = Blueprint(
    'background_jobs', __name__, url_prefix='/background_jobs')


@background_jobs_controller.route('/', methods=["GET"])
def get_background_jobs():
    db = get_services(current_app).db.connection

    background_jobs = []
    for background_job in db["background_jobs"].find():
        background_job["_id"] = str(background_job["_id"])
        background_jobs.append(background_job)

    return respond_success(background_jobs, status_code=200)


@background_jobs_controller.route('/', methods=["POST"])
def create_background_job():
    data = request.get_json()

    background_job_model = get_models(current_app).background_jobs
    if data is None or not all(key in data for key in ('type', 'metadata')):
        return respond_error("Bad request.", 400)

    background_job_data = BackgroundJobCreate(
        type=data["type"],
        metadata=data["metadata"],
        created_by="admin"
    )

    background_job = background_job_model.create(background_job_data)

    return respond_success(background_job.to_json(), status_code=200)


