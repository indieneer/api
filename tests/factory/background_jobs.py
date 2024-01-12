from app.models import ModelsExtension, BackgroundJobsModel
from app.models.background_jobs import BackgroundJobCreate, BackgroundJob
from app.services import Database
from bson import ObjectId
from typing import Union


class BackgroundJobsFactory:
    db: Database
    model: BackgroundJobsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, background_job_id: ObjectId):
        self.db.connection[self.models.background_jobs.collection].delete_one({
            "_id": background_job_id})

    def create(self, input_data: Union[BackgroundJob, BackgroundJobCreate]):
        if isinstance(input_data, BackgroundJob):
            background_job = self.models.background_jobs.put(input_data)
        else:
            background_job = self.models.background_jobs.create(input_data)

        return background_job, lambda: self.cleanup(background_job._id)
