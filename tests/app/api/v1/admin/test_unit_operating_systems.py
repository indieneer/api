from unittest.mock import patch, MagicMock
import json
from app.api.v1.admin.operating_systems import create_operating_system, delete_operating_system, update_operating_system, get_operating_system_by_id

from tests import UnitTest
from app.models.operating_systems import OperatingSystemCreate, OperatingSystem, OperatingSystemPatch
from tests.utils.jwt import create_test_token


class OperatingSystemsTestCase(UnitTest):

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_create_operating_system(self, get_models: MagicMock):
        endpoint = "/operating-systems"
        self.app.route(endpoint, methods=["POST"])(create_operating_system)

        create_os_mock = get_models.return_value.operating_systems.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_an_operating_system():
            # given
            mock_os = OperatingSystem(name="Windows")
            create_os_mock.return_value = mock_os

            expected_input = OperatingSystemCreate(name=mock_os.name)
            expected_response = {
                "status": "ok",
                "data": mock_os.to_json()
            }

            # when
            response = call_api({"name": expected_input.name})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_os_mock.assert_called_once_with(expected_input)

        def fails_to_create_an_operating_system_and_returns_an_error():
            # given
            create_os_mock.side_effect = Exception("Error creating OS")

            # when
            with self.assertRaises(Exception) as context:
                call_api({"name": "Invalid OS"})

            # then
            self.assertEqual(str(context.exception),
                             str(create_os_mock.side_effect))
            create_os_mock.assert_called_once()

        def fails_to_create_an_operating_system_when_body_is_invalid():
            # when
            with self.assertRaises(Exception) as context:
                call_api({"invalid_field": "value"})

            # then
            self.assertEqual(str(context.exception), "Invalid data provided.")
            create_os_mock.assert_not_called()

        tests = [
            creates_and_returns_an_operating_system,
            fails_to_create_an_operating_system_and_returns_an_error,
            fails_to_create_an_operating_system_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_os_mock.reset_mock)

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_get_operating_system(self, get_models: MagicMock):
        endpoint = "/operating-systems/<string:operating_system_id>"
        self.app.route(endpoint)(get_operating_system_by_id)

        get_os_mock = get_models.return_value.operating_systems.get

        def call_api(os_id):
            return self.test_client.get(
                endpoint.replace("<string:operating_system_id>", str(os_id)),
                headers={
                    "Authorization": "Bearer " + create_test_token("", roles=["admin"])
                },
                content_type='application/json'
            )

        def finds_and_returns_an_operating_system():
            # given
            mock_os = OperatingSystem(name="Windows")
            get_os_mock.return_value = mock_os

            expected_response = {
                "status": "ok",
                "data": mock_os.to_json()
            }

            # when
            response = call_api(mock_os._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_os_mock.assert_called_once_with(str(mock_os._id))

        def does_not_find_an_operating_system_and_returns_an_error():
            # given
            mock_id = "123"
            get_os_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'The operating system with ID {mock_id} was not found.'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_os_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_an_operating_system,
            does_not_find_an_operating_system_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_os_mock.reset_mock)

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_patch_operating_system(self, get_models: MagicMock):
        endpoint = "/operating-systems/<string:operating_system_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_operating_system)

        patch_os_mock = get_models.return_value.operating_systems.patch

        def call_api(os_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:operating_system_id>", str(os_id)),
                data=json.dumps(body),
                headers={
                    "Authorization": "Bearer " + create_test_token("", roles=["admin"])
                },
                content_type='application/json'
            )

        def patches_and_returns_the_operating_system():
            # given
            mock_os = OperatingSystem(name="Windows")
            patch_os_mock.return_value = mock_os

            expected_input = OperatingSystemPatch(name="Updated Windows")
            expected_response = {
                "status": "ok",
                "data": mock_os.to_json()
            }

            # when
            response = call_api(mock_os._id, {"name": expected_input.name})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            patch_os_mock.assert_called_once_with(
                str(mock_os._id),
                expected_input
            )

        def fails_to_patch_a_nonexistent_operating_system():
            # given
            mock_id = "123"
            patch_os_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"The operating system with ID {mock_id} was not found."
            }

            # when
            response = call_api(mock_id, {"name": "Nonexistent OS"})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            patch_os_mock.assert_called_once_with(
                str(mock_id),
                OperatingSystemPatch(name='Nonexistent OS')
            )

        tests = [
            patches_and_returns_the_operating_system,
            fails_to_patch_a_nonexistent_operating_system
        ]

        self.run_subtests(tests, after_each=patch_os_mock.reset_mock)

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_delete_operating_system(self, get_models: MagicMock):
        endpoint = "/operating-systems/<string:operating_system_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_operating_system)

        delete_os_mock = get_models.return_value.operating_systems.delete

        def call_api(os_id):
            return self.test_client.delete(
                endpoint.replace("<string:operating_system_id>", str(os_id)),
                headers={
                    "Authorization": "Bearer " + create_test_token("", roles=["admin"])
                },
                content_type='application/json'
            )

        def deletes_the_operating_system():
            # given
            mock_os = OperatingSystem(name="Windows")
            delete_os_mock.return_value = mock_os

            expected_response = {
                "status": "ok",
                "data": {"deleted_os": mock_os.to_json(), "message": f'Operating system id {mock_os._id} successfully deleted'}
            }

            # when
            response = call_api(mock_os._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            delete_os_mock.assert_called_once_with(str(mock_os._id))

        def fails_to_delete_a_nonexistent_operating_system():
            # given
            mock_id = "123"
            delete_os_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"The operating system with ID {mock_id} was not found."
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_os_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_operating_system,
            fails_to_delete_a_nonexistent_operating_system
        ]

        self.run_subtests(tests, after_each=delete_os_mock.reset_mock)

