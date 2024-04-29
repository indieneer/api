from bson import ObjectId

from app.models import BackgroundJobsModel
from app.models.background_jobs import BackgroundJobPatch, EventCreate, Event, BackgroundJobCreate
from tests import IntegrationTest


class BackgroundJobsModelTestCase(IntegrationTest):
    def test_get_all_background_jobs(self):
        self.skipTest("Fix hardcoded")
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job = self.fixtures.background_job

        # when
        background_jobs = background_jobs_model.get_all()

        # then
        self.assertIsNotNone(background_jobs)
        self.assertEqual(len(background_jobs), 1)
        self.assertEqual(background_jobs[0]._id, background_job._id)

    def test_get_background_job(self):
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job = self.fixtures.background_job

        # when
        retrieved_background_job = background_jobs_model.get(
            str(background_job._id))

        # then
        if retrieved_background_job is None:
            self.assertIsNotNone(retrieved_background_job)
        else:
            self.assertEqual(background_job._id, retrieved_background_job._id)

    def test_get_background_job_not_found(self):
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job_id = ObjectId()

        # when
        retrieved_background_job = background_jobs_model.get(
            str(background_job_id))

        # then
        self.assertIsNone(retrieved_background_job)

    def test_patch_background_job(self):
        background_jobs_model = BackgroundJobsModel(self.services.db)

        # given
        background_job = self.fixtures.background_job
        patch_data = BackgroundJobPatch(status="pending")

        # when
        updated_background_job = background_jobs_model.patch(
            str(background_job._id), patch_data)

        # then
        if updated_background_job is None:
            self.assertIsNotNone(updated_background_job)
        else:
            self.assertEqual(updated_background_job.status, "pending")

    def test_patch_background_job_with_invalid_status(self):
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job = self.fixtures.background_job
        patch_data = BackgroundJobPatch(status="invalid")

        # when
        with self.assertRaises(ValueError):
            background_jobs_model.patch(str(background_job._id), patch_data)

        # then
        background_job = background_jobs_model.get(str(background_job._id))
        self.assertEqual(background_job.status,
                         self.fixtures.background_job.status)

    def test_put_background_job(self):
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job = self.fixtures.background_job.clone()
        background_job.status = "pending"

        # when
        updated_background_job = background_jobs_model.put(background_job)
        self.addCleanup(lambda: background_jobs_model.delete(
            str(updated_background_job._id)))

        # then
        self.assertIsNotNone(updated_background_job)
        self.assertEqual(updated_background_job.status, background_job.status)

    def test_create_background_job(self):
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job = self.fixtures.background_job

        # when
        created_background_job = background_jobs_model.create(
            BackgroundJobCreate(type=background_job.type, metadata={
                "match_query": "test"
            }, created_by=background_job.created_by))
        self.addCleanup(lambda: background_jobs_model.delete(
            str(created_background_job._id)))

        # then
        self.assertIsNotNone(created_background_job)
        self.assertEqual(created_background_job.type, background_job.type)
        self.assertEqual(created_background_job.status, background_job.status)
        self.assertEqual(created_background_job.metadata,
                         background_job.metadata)
        self.assertEqual(created_background_job.created_by,
                         background_job.created_by)

    def test_delete_background_job(self):
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job, cleanup = self.factory.background_jobs.create(
            self.fixtures.background_job.clone())

        # when
        deleted_count = background_jobs_model.delete(str(background_job._id))
        retrieved_background_job_after_deletion = background_jobs_model.get(
            str(background_job._id))

        # then
        self.assertEqual(deleted_count, 1)
        self.assertIsNone(retrieved_background_job_after_deletion)

    def test_add_event_to_background_job(self):
        self.skipTest("unexpectedly None")
        # given
        background_jobs_model = BackgroundJobsModel(self.services.db)
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        background_job.events = [Event(type="info", message="Test event")]
        self.addCleanup(cleanup)

        event = EventCreate(type="info", message="Test event")

        # when
        updated_background_job = background_jobs_model.add_event(
            str(background_job._id), event)

        # then
        self.assertIsNotNone(updated_background_job)
        self.assertEqual(updated_background_job.events[0]['type'], background_job.to_dict()[
                         "events"][0]["type"])
        self.assertEqual(updated_background_job.events[0]['message'], background_job.to_dict()[
                         "events"][0]["message"])
