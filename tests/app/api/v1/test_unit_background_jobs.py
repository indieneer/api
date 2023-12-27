import json
from unittest.mock import MagicMock, patch

from app.middlewares.requires_auth import create_test_token
from app.models.background_jobs import BackgroundJob, BackgroundJobCreate, BackgroundJobPatch, EventCreate, Event
from tests import UnitTest


class BackgroundJobsTestCase(UnitTest):
    @patch("app.api.v1.background_jobs.get_models")
    def test_get_background_job(self, get_models: MagicMock):
        get_background_job_mock = get_models.return_value.background_jobs.get

        def call_api(background_job_id):
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.app.get(f"/v1/background_jobs/{background_job_id}",
                                headers={"Authorization": f"Bearer {token}"},
                                content_type='application/json')

        def finds_and_returns_a_background_job():
            # given
            mock_background_job = BackgroundJob(
                status="running", created_by="service_test@clients", metadata={"match_query": "test"},
                type="es_seeder")
            get_background_job_mock.return_value = mock_background_job

            expected_response = {
                "status": "ok",
                "data": mock_background_job.to_json()
            }

            # when
            response = call_api(mock_background_job._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_background_job_mock.assert_called_once_with(mock_background_job._id)

        def does_not_find_a_background_job_and_returns_an_error():
            # given
            mock_id = "1"
            get_background_job_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": "\"BackgroundJob\" not found."
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_background_job_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_background_job,
            does_not_find_a_background_job_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                get_background_job_mock.reset_mock()

    @patch("app.api.v1.background_jobs.get_models")
    def test_get_all_background_jobs(self, get_models: MagicMock):
        get_all_background_jobs_mock = get_models.return_value.background_jobs.get_all

        def call_api():
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.app.get(f"/v1/background_jobs",
                                headers={"Authorization": f"Bearer {token}"},
                                content_type='application/json')

        def finds_and_returns_all_background_jobs():
            # given
            mock_background_jobs = [
                BackgroundJob(
                    status="running", created_by="service_test@clients", metadata={"match_query": "test"},
                    type="es_seeder"),
                BackgroundJob(
                    status="running", created_by="service_test@clients", metadata={"match_query": "test"},
                    type="es_seeder")
            ]
            get_all_background_jobs_mock.return_value = mock_background_jobs

            expected_response = {
                "status": "ok",
                "data": [background_job.to_json() for background_job in mock_background_jobs]
            }

            # when
            response = call_api()

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_all_background_jobs_mock.assert_called_once()

        tests = [
            finds_and_returns_all_background_jobs,
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                get_all_background_jobs_mock.reset_mock()

    @patch("app.api.v1.background_jobs.get_models")
    def test_create_background_job(self, get_models: MagicMock):
        create_background_job_mock = get_models.return_value.background_jobs.create

        def call_api(body):
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.app.post(
                "/v1/background_jobs",
                data=json.dumps(body),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def create_and_returns_a_background_job():
            # given
            mock_background_job = BackgroundJob(
                status="running", created_by="service_test@clients", metadata={"match_query": "test"},
                type="es_seeder")
            create_background_job_mock.return_value = mock_background_job

            expected_input = BackgroundJobCreate(
                type="es_seeder", metadata={"match_query": "test"}, created_by="service_test@clients"
            )
            expected_response = {
                "status": "ok",
                "data": mock_background_job.to_json()
            }

            # when
            response = call_api({
                "type": "es_seeder",
                "metadata": {"match_query": "test"}
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_background_job_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_background_job_when_not_all_required_fields_are_present():
            # given
            expected_response = {
                "error": "Not all required fields are present",
                "status": "error"
            }

            # when
            response = call_api({
                "type": "es_seeder"
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            create_background_job_mock.assert_not_called()

        def fails_to_create_a_background_job_when_type_is_not_supported():
            # given
            expected_response = {
                "error": "Unsupported job type",
                "status": "error"
            }

            # when
            response = call_api({
                "type": "unsupported_type",
                "metadata": {}
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            create_background_job_mock.assert_not_called()

        tests = [
            create_and_returns_a_background_job,
            fails_to_create_a_background_job_when_not_all_required_fields_are_present,
            fails_to_create_a_background_job_when_type_is_not_supported
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                create_background_job_mock.reset_mock()

    @patch("app.api.v1.background_jobs.get_models")
    def test_patch_background_job(self, get_models: MagicMock):
        patch_background_job_mock = get_models.return_value.background_jobs.patch

        def call_api(background_job_id, body):
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.app.patch(
                f"/v1/background_jobs/{background_job_id}",
                data=json.dumps(body),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def patches_and_returns_a_background_job():
            # given
            mock_background_job = BackgroundJob(
                status="running", created_by="service_test@clients", metadata={"match_query": "test"},
                type="es_seeder")
            patch_background_job_mock.return_value = mock_background_job

            expected_input = BackgroundJobPatch(
                status="running"
            )
            expected_response = {
                "status": "ok",
                "data": mock_background_job.to_json()
            }

            # when
            response = call_api(mock_background_job._id, {
                "status": mock_background_job.status
            })
            print(response.get_json())
            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            patch_background_job_mock.assert_called_once_with(mock_background_job._id, expected_input)

        def fails_to_update_a_background_job_when_no_valid_fields_are_present():
            # given
            expected_response = {
                "error": "No valid fields are present",
                "status": "error"
            }

            # when
            response = call_api("1", {})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            patch_background_job_mock.assert_not_called()

        def fails_to_update_a_background_job_when_background_job_does_not_exist():
            # given
            mock_id = "1"
            patch_background_job_mock.return_value = None

            expected_response = {
                "error": "\"BackgroundJob\" not found.",
                "status": "error"
            }

            # when
            response = call_api(mock_id, {"status": "running"})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            patch_background_job_mock.assert_called_once_with(mock_id)

        tests = [
            patches_and_returns_a_background_job,
            fails_to_update_a_background_job_when_no_valid_fields_are_present,
            fails_to_update_a_background_job_when_background_job_does_not_exist
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                patch_background_job_mock.reset_mock()

    @patch("app.api.v1.background_jobs.get_models")
    def test_create_background_job_event(self, get_models: MagicMock):
        create_background_job_event_mock = get_models.return_value.background_jobs.add_event

        def call_api(background_job_id, body):
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.app.post(
                f"/v1/background_jobs/{background_job_id}/events",
                data=json.dumps(body),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def create_and_returns_a_background_job_event():
            # given
            mock_background_job = BackgroundJob(
                status="running", created_by="service_test@clients", metadata={"match_query": "test"},
                type="es_seeder", events=[Event(
                    message="test",
                    type="info"
                )])
            create_background_job_event_mock.return_value = mock_background_job

            expected_input = Event(
                message="test",
                type="info"
            )
            expected_response = {
                "status": "ok",
                "data": mock_background_job.to_json()
            }

            # when
            response = call_api(mock_background_job._id, {
                "type": "info",
                "message": "hello"
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            create_background_job_event_mock.assert_called_once_with(mock_background_job._id, expected_input)

        tests = [
            create_and_returns_a_background_job_event
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                create_background_job_event_mock.reset_mock()
