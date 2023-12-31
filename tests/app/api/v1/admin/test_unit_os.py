from unittest.mock import patch, MagicMock
import json

from tests import UnitTest
from app.models.operating_systems import OperatingSystemCreate, OperatingSystem, OperatingSystemPatch
from tests.utils.jwt import create_test_token


class OperatingSystemsTestCase(UnitTest):

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_create_operating_system(self, get_models: MagicMock):
        create_os_mock = get_models.return_value.operating_systems.create

        def call_api(body):
            return self.app.post(
                "/v1/admin/operating-systems",
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])}
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

            expected_response = {
                "status": "error",
                "error": "Error creating OS"
            }

            # when
            response = call_api({"name": "Invalid OS"})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 500)
            create_os_mock.assert_called_once()

        def fails_to_create_an_operating_system_when_body_is_invalid():
            # given
            expected_response = {
                "status": "error",
                "error": "Invalid data provided."
            }

            # when
            response = call_api({"invalid_field": "value"})

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            create_os_mock.assert_not_called()

        tests = [
            creates_and_returns_an_operating_system,
            fails_to_create_an_operating_system_and_returns_an_error,
            fails_to_create_an_operating_system_when_body_is_invalid
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            create_os_mock.reset_mock()

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_get_operating_system(self, get_models: MagicMock):
        get_os_mock = get_models.return_value.operating_systems.get

        def call_api(os_id):
            return self.app.get(
                f"/v1/admin/operating-systems/{os_id}",
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
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
            get_os_mock.assert_called_once_with(mock_os._id)

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

        for test in [finds_and_returns_an_operating_system, does_not_find_an_operating_system_and_returns_an_error]:
            with self.subTest(test.__name__):
                test()
            get_os_mock.reset_mock()

    @patch("app.api.v1.admin.operating_systems.get_models")
    def test_delete_operating_system(self, get_models: MagicMock):
        delete_os_mock = get_models.return_value.operating_systems.delete

        def call_api(os_id):
            return self.app.delete(
                f"/v1/admin/operating-systems/{os_id}",
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
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
            delete_os_mock.assert_called_once_with(mock_os._id)

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

        for test in [deletes_the_operating_system, fails_to_delete_a_nonexistent_operating_system]:
            with self.subTest(test.__name__):
                test()
            delete_os_mock.reset_mock()