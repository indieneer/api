from bson import ObjectId

from app.models.background_jobs import BackgroundJobCreate
from config import app_config
from tests import IntegrationTest


class BackgroundJobsTestCase(IntegrationTest):
    @property
    def token(self):
        return self.models.logins.login_m2m("bUhOAswerBbA3lamY0saxLuJezB7sjOs",
                                            app_config["AUTH0_CLIENT_SECRET"])["access_token"]

    def test_get_all_background_jobs(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        _, cleanup = self.factory.background_jobs.create(BackgroundJobCreate(type="es_seeder", metadata={
            "match_query": "test"
        }, created_by="service_test@clients"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(
            '/v1/background_jobs',
            headers={
                "Authorization": f"Bearer {self.token}"
            })
        response_json = response.get_json()

        # then
        self.assertEqual(type(response_json["data"]), list)
        self.assertEqual(len(response_json["data"]), 2)

    def test_get_background_job_by_id(self):
        self.skipTest("Fix when Firebase auth implemented")
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
        self.skipTest("Fix when Firebase auth implemented")
        # when
        response = self.app.get(
            f'/v1/background_jobs/{ObjectId()}',
            headers={"Authorization": f"Bearer {self.token}"
                     }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"],
                         "\"BackgroundJob\" not found.")
        self.assertEqual(response.status_code, 404)

    def test_get_background_job_by_id_without_auth_header(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        background_job_id = background_job._id
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(
            f'/v1/background_jobs/{background_job_id}'
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"]
                         ["code"], "authorization_header_missing")
        self.assertEqual(response.status_code, 401)

    def test_get_background_job_by_id_without_permission(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        user = self.fixtures.regular_user.clone()
        token = self.factory.logins.login(
            user.email, "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")["access_token"]

        # when
        response = self.app.get(
            f'/v1/background_jobs/{self.fixtures.background_job._id}',
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        # then
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"], "no permission")

    def test_create_background_job(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        data = {
            "type": "es_seeder",
            "metadata": {
                "match_query": "test_create_background_job"
            }
        }

        # when
        response = self.app.post(
            '/v1/background_jobs',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(type(response_json["data"]), dict)
        self.assertEqual(response_json["data"]["type"], data["type"])
        self.assertEqual(response_json["data"]["metadata"], data["metadata"])

        self.factory.background_jobs.cleanup(
            ObjectId(response_json["data"]["_id"]))

    def test_create_background_job_without_all_required_fields_present(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        data = {
            "type": "es_seeder"
        }

        # when
        response = self.app.post(
            '/v1/background_jobs',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"],
                         "Not all required fields are present")
        self.assertEqual(response.status_code, 400)

    def test_create_background_job_with_invalid_type(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        data = {
            "type": "invalid_type",
            "metadata": {
                "match_query": "test_create_background_job"
            }
        }

        # when
        response = self.app.post(
            '/v1/background_jobs',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"], "Unsupported job type")
        self.assertEqual(response.status_code, 400)

    def test_update_background_job(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "status": "pending"
        }

        # when
        response = self.app.patch(
            f'/v1/background_jobs/{background_job._id}',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(type(response_json["data"]), dict)
        self.assertEqual(response_json["data"]["status"], data["status"])

    def test_update_background_job_with_no_valid_fields_present(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "invalid_field": "pending"
        }

        # when
        response = self.app.patch(
            f'/v1/background_jobs/{background_job._id}',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"], "No valid fields are present")
        self.assertEqual(response.status_code, 400)

    def test_update_background_job_with_invalid_status(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "status": "invalid_status"
        }

        # when
        response = self.app.patch(
            f'/v1/background_jobs/{background_job._id}',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"], "Unsupported status")
        self.assertEqual(response.status_code, 400)

    def test_update_background_job_with_invalid_id(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        data = {
            "status": "pending"
        }

        # when
        response = self.app.patch(
            f'/v1/background_jobs/{ObjectId()}',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"],
                         "\"BackgroundJob\" not found.")
        self.assertEqual(response.status_code, 404)

    def test_update_background_job_with_valid_and_invalid_fields_present(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "status": "pending",
            "invalid_field": "pending"
        }

        # when
        response = self.app.patch(
            f'/v1/background_jobs/{background_job._id}',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"], "Bad request.")
        self.assertEqual(response.status_code, 400)

    def test_update_background_job_when_was_created_by_another_user(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        background_job.created_by = "another_user@clients"
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "status": "pending"
        }

        # when
        response = self.app.patch(
            f'/v1/background_jobs/{background_job._id}',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )

        # then
        self.assertEqual(response.get_json()["error"], "Forbidden.")
        self.assertEqual(response.status_code, 403)

    def test_create_background_job_event(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "type": "info",
            "message": "Test event"
        }

        # when
        response = self.app.post(
            f'/v1/background_jobs/{background_job._id}/events',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(type(response_json["data"]), dict)
        self.assertEqual(response_json["data"]
                         ["events"][0]["type"], data["type"])
        self.assertEqual(response_json["data"]
                         ["events"][0]["message"], data["message"])
        self.assertEqual(len(response_json["data"]["events"]), 1)

    def test_create_background_job_event_with_not_all_required_fields_present(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "type": "info"
        }

        # when
        response = self.app.post(
            f'/v1/background_jobs/{background_job._id}/events',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response_json["error"],
                         "Not all required fields are present")
        self.assertEqual(response.status_code, 400)

    def test_create_background_job_event_with_invalid_id(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        data = {
            "type": "info",
            "message": "Test event"
        }

        # when
        response = self.app.post(
            f'/v1/background_jobs/{ObjectId()}/events',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )

        # then
        self.assertEqual(response.get_json()[
                         "error"], "\"BackgroundJob\" not found.")
        self.assertEqual(response.status_code, 404)

    def test_create_background_job_event_when_was_created_by_another_user(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        background_job.created_by = "another_user@clients"
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "type": "info",
            "message": "Test event"
        }

        # when
        response = self.app.post(
            f'/v1/background_jobs/{background_job._id}/events',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )

        # then
        self.assertEqual(response.get_json()["error"], "Forbidden.")
        self.assertEqual(response.status_code, 403)

    def test_create_background_job_event_with_invalid_event_type(self):
        self.skipTest("Fix when Firebase auth implemented")
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        data = {
            "type": "invalid_type",
            "message": "Test event"
        }

        # when
        response = self.app.post(
            f'/v1/background_jobs/{background_job._id}/events',
            json=data,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )

        # then
        self.assertEqual(response.get_json()[
                         "error"], "Unsupported event type")
        self.assertEqual(response.status_code, 400)
