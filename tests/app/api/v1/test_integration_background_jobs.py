from app.middlewares.requires_auth import create_test_token
from tests import IntegrationTest


class BackgroundJobsTestCase(IntegrationTest):
    token = create_test_token(profile_id="1", idp_id="service_test@clients")

    def test_get_all_background_jobs(self):
        # given
        self.factory.background_jobs.create(self.fixtures.background_job.clone())
        self.factory.background_jobs.create(self.fixtures.background_job.clone())

        # when
        response = self.app.get(
            '/v1/background_jobs',
            headers={
                "Authorization": f"Bearer {self.token}"
            })
        response_json = response.get_json()

        # then
        self.assertEqual(type(response_json["data"]), list)
        self.assertGreater(len(response_json["data"]), 0)

    def test_get_background_job_by_id(self):
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(
            f'/v1/background_jobs/{background_job._id}',
            headers={
                "Authorization": f"Bearer {self.token}"
            })
        response_json = response.get_json()

        # then
        self.assertEqual(type(response_json["data"]), dict)
        self.assertEqual(response_json["data"]["_id"], str(background_job._id))

    def test_get_background_job_by_id_not_found(self):
        # given
        background_job = self.fixtures.background_job.clone()
        background_job_id = background_job._id
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)
        cleanup()

        # when
        response = self.app.get(
            f'/v1/background_jobs/{background_job_id}',
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"], "\"BackgroundJob\" not found.")
        self.assertEqual(response.status_code, 404)

    def test_get_background_job_by_id_without_auth_header(self):
        # given
        background_job = self.fixtures.background_job.clone()
        background_job_id = background_job._id
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)
        cleanup()

        # when
        response = self.app.get(
            f'/v1/background_jobs/{background_job_id}'
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"]["code"], "authorization_header_missing")
        self.assertEqual(response.status_code, 401)
