from app.models import BackgroundJobsModel
from app.models.background_jobs import BackgroundJobPatch, EventCreate, Event
from tests import IntegrationTest


class BackgroundJobsModelTestCase(IntegrationTest):
    def test_get_background_job(self):
        background_jobs_model = BackgroundJobsModel(self.services.db)

        # given
        background_job = self.fixtures.background_job

        # when
        retrieved_background_job = background_jobs_model.get(str(background_job._id))

        # then
        if retrieved_background_job is None:
            self.assertIsNotNone(retrieved_background_job)
        else:
            self.assertEqual(background_job._id, retrieved_background_job._id)

    def test_patch_background_job(self):
        background_jobs_model = BackgroundJobsModel(self.services.db)

        # given
        background_job = self.fixtures.background_job
        patch_data = BackgroundJobPatch(status="pending")

        # when
        updated_background_job = background_jobs_model.patch(str(background_job._id), patch_data)

        # then
        if updated_background_job is None:
            self.assertIsNotNone(updated_background_job)
        else:
            self.assertEqual(updated_background_job.status, "pending")

    def test_delete_background_job(self):
        background_jobs_model = BackgroundJobsModel(self.services.db)

        # given
        background_job, cleanup = self.factory.background_jobs.create(
            self.fixtures.background_job.clone())
        self.addCleanup(cleanup)

        # when
        deleted_count = background_jobs_model.delete(str(background_job._id))
        retrieved_background_job_after_deletion = background_jobs_model.get(str(background_job._id))

        # then
        self.assertEqual(deleted_count, 1)
        self.assertIsNone(retrieved_background_job_after_deletion)

    def test_add_event_to_background_job(self):
        background_jobs_model = BackgroundJobsModel(self.services.db)

        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        background_job.events = [Event(type="info", message="Test event")]
        self.addCleanup(cleanup)

        event = EventCreate(type="info", message="Test event")

        # when
        updated_background_job = background_jobs_model.add_event(str(background_job._id), event)

        # then
        if updated_background_job is None:
            self.assertIsNotNone(updated_background_job)
        else:
            self.assertEqual(updated_background_job.events[0]['type'], background_job.to_dict()["events"][0]["type"])
            self.assertEqual(updated_background_job.events[0]['message'], background_job.to_dict()["events"][0]["message"])
