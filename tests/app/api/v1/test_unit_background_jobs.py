import json
from unittest.mock import MagicMock, patch

from app.models.background_jobs import BackgroundJob, BackgroundJobCreate, BackgroundJobPatch, EventCreate, Event
from tests import UnitTest
from tests.utils.jwt import create_test_token


class BackgroundJobsTestCase(UnitTest):
    @patch("app.api.v1.background_jobs.get_models")
    def test_get_background_job(self, get_models: MagicMock):
        get_background_job_mock = get_models.return_value.background_jobs.get

        def call_api(background_job_id):
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.test_client.get(f"/v1/background_jobs/{background_job_id}",
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

        def finds_a_background_job_with_another_creator_and_returns_an_error():
            # given
            mock_background_job = BackgroundJob(
                status="running", created_by="someone_else", metadata={"match_query": "test"},
                type="es_seeder")
            get_background_job_mock.return_value = mock_background_job

            expected_response = {
                "status": "error",
                "error": "Forbidden."
            }

            # when
            response = call_api(mock_background_job._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 403)
            get_background_job_mock.assert_called_once_with(str(mock_background_job._id))

        tests = [
            finds_and_returns_a_background_job,
            does_not_find_a_background_job_and_returns_an_error,
            finds_a_background_job_with_another_creator_and_returns_an_error
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

            return self.test_client.get(f"/v1/background_jobs",
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
        service_account_id = "service_test@clients"

        def call_api(body):
            token = create_test_token(profile_id="1", idp_id=service_account_id)

            return self.test_client.post(
                "/v1/background_jobs",
                data=json.dumps(body),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def creates_and_returns_a_background_job():
            # given
            expected_input = BackgroundJobCreate(
                type="es_seeder", metadata={"match_query": "test"}, created_by=service_account_id
            )
            mock_background_job = BackgroundJob(
                status="running",
                created_by=expected_input.created_by,
                metadata=expected_input.metadata,
                type=expected_input.type
            )
            create_background_job_mock.return_value = mock_background_job

            expected_response = {
                "status": "ok",
                "data": mock_background_job.to_json()
            }

            # when
            response = call_api({
                "type": "es_seeder",
                "metadata": expected_input.metadata
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
            expected_input = BackgroundJobCreate(type="unsupported_type", metadata={}, created_by=service_account_id)
            create_background_job_mock.side_effect = ValueError(expected_response["error"])

            # when
            response = call_api({
                "type": expected_input.type,
                "metadata": expected_input.metadata
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            create_background_job_mock.assert_called_once_with(expected_input)

        tests = [
            creates_and_returns_a_background_job,
            fails_to_create_a_background_job_when_not_all_required_fields_are_present,
            fails_to_create_a_background_job_when_type_is_not_supported
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            create_background_job_mock.reset_mock()

    @patch("app.api.v1.background_jobs.get_models")
    def test_update_background_job(self, get_models: MagicMock):
        get_background_job_mock = get_models.return_value.background_jobs.get
        patch_background_job_mock = get_models.return_value.background_jobs.patch

        def call_api(background_job_id, body):
            token = create_test_token(profile_id="1", idp_id="service_test@clients")

            return self.test_client.patch(
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
            get_background_job_mock.return_value = mock_background_job
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

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_background_job_mock.assert_called_once_with(mock_background_job._id)
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
            get_background_job_mock.return_value = None

            expected_response = {
                "error": "\"BackgroundJob\" not found.",
                "status": "error"
            }

            # when
            response = call_api(mock_id, {"status": "running"})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_background_job_mock.assert_called_once_with(mock_id)

        def fails_to_update_a_background_job_when_was_created_by_another_user():
            # given
            mock_background_job = BackgroundJob(
                status="running", created_by="someone_else", metadata={"match_query": "test"},
                type="es_seeder")
            get_background_job_mock.return_value = mock_background_job

            expected_response = {
                "error": "Forbidden.",
                "status": "error"
            }

            # when
            response = call_api(mock_background_job._id, {"status": "running"})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 403)
            get_background_job_mock.assert_called_once_with(str(mock_background_job._id))
            patch_background_job_mock.assert_not_called()

        tests = [
            patches_and_returns_a_background_job,
            fails_to_update_a_background_job_when_no_valid_fields_are_present,
            fails_to_update_a_background_job_when_background_job_does_not_exist,
            fails_to_update_a_background_job_when_was_created_by_another_user
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_background_job_mock.reset_mock()
            patch_background_job_mock.reset_mock()

    @patch("app.api.v1.background_jobs.get_models")
    def test_create_background_job_event(self, get_models: MagicMock):
        get_background_job_mock = get_models.return_value.background_jobs.get
        add_background_job_event_mock = get_models.return_value.background_jobs.add_event
        service_account_id = "service_test@clients"

        def call_api(background_job_id, body):
            token = create_test_token(profile_id="1", idp_id=service_account_id)

            return self.test_client.post(
                f"/v1/background_jobs/{background_job_id}/events",
                data=json.dumps(body),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def creates_and_returns_a_background_job_event():
            # given
            mock_event = Event(message="test", type="info")
            mock_background_job = BackgroundJob(
                status="running", created_by=service_account_id, metadata={"match_query": "test"},
                type="es_seeder", events=[mock_event])

            get_background_job_mock.return_value = mock_background_job
            add_background_job_event_mock.return_value = mock_background_job

            expected_input = EventCreate(message=mock_event.message, type=mock_event.type)
            expected_response = {
                "status": "ok",
                "data": mock_background_job.to_json()
            }

            # when
            response = call_api(mock_background_job._id, {
                "type": mock_event.type,
                "message": mock_event.message
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            add_background_job_event_mock.assert_called_once_with(mock_background_job._id, expected_input)

        def fails_to_create_a_background_job_event_when_not_all_required_fields_are_present():
            # given
            expected_response = {
                "error": "Not all required fields are present",
                "status": "error"
            }

            # when
            response = call_api("1", {
                "type": "info"
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            add_background_job_event_mock.assert_not_called()

        def fails_to_create_a_background_job_event_when_job_was_created_by_another_user():
            # given
            mock_event = Event(message="test", type="info")
            mock_background_job = BackgroundJob(
                status="running", created_by="someone_else", metadata={"match_query": "test"},
                type="es_seeder", events=[mock_event])

            get_background_job_mock.return_value = mock_background_job
            add_background_job_event_mock.return_value = mock_background_job

            expected_response = {
                "error": "Forbidden.",
                "status": "error"
            }

            # when
            response = call_api(mock_background_job._id, {
                "type": mock_event.type,
                "message": mock_event.message
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 403)
            get_background_job_mock.assert_called_once_with(str(mock_background_job._id))
            add_background_job_event_mock.assert_not_called()

        def fails_to_create_a_background_job_event_when_background_job_does_not_exist():
            # given
            mock_id = "1"
            get_background_job_mock.return_value = None

            expected_response = {
                "error": "\"BackgroundJob\" not found.",
                "status": "error"
            }

            # when
            response = call_api(mock_id, {
                "type": "info",
                "message": "test"
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_background_job_mock.assert_called_once_with(mock_id)
            add_background_job_event_mock.assert_not_called()

        def fails_to_create_a_background_job_event_when_event_type_is_not_supported():
            # given
            mock_event_create = EventCreate(type="unsupported_type", message="test")
            mock_background_job = BackgroundJob(
                status="running", created_by=service_account_id, metadata={"match_query": "test"},
                type="es_seeder")

            get_background_job_mock.return_value = mock_background_job

            expected_response = {
                "error": "Unsupported event type",
                "status": "error"
            }
            add_background_job_event_mock.side_effect = ValueError(expected_response["error"])

            # when
            response = call_api(mock_background_job._id, {
                "type": mock_event_create.type,
                "message": mock_event_create.message
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            get_background_job_mock.assert_called_once_with(str(mock_background_job._id))
            add_background_job_event_mock.assert_called_once_with(str(mock_background_job._id), mock_event_create)

        tests = [
            creates_and_returns_a_background_job_event,
            fails_to_create_a_background_job_event_when_not_all_required_fields_are_present,
            fails_to_create_a_background_job_event_when_job_was_created_by_another_user,
            fails_to_create_a_background_job_event_when_background_job_does_not_exist,
            fails_to_create_a_background_job_event_when_event_type_is_not_supported
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_background_job_mock.reset_mock()
            add_background_job_event_mock.reset_mock()
