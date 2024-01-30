from unittest.mock import patch

from pymongo.errors import ServerSelectionTimeoutError
from app.api.v1.health import health

from tests import UnitTest
from tests.mocks.services import mock_database_connection


class HealthTestCase(UnitTest):

    @patch("app.api.v1.health.app_config")
    @patch("app.api.v1.health.get_services")
    def test_get_health(self, get_services, app_config):
        # given
        endpoint = "/health"
        self.app.route(endpoint)(health)

        connection = mock_database_connection(get_services)

        mock_config = {"ENVIRONMENT": "production", "VERSION": "4.3.1"}
        connection.command.return_value = {"ok": 1}
        app_config.get.side_effect = lambda key: mock_config[key]

        # when
        response = self.test_client.get(endpoint)

        # then
        expected = {
            "status": "ok",
            "data": {
                "db": 1,
                "env": "production",
                "version": "4.3.1"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)

    @patch("app.api.v1.health.app_config")
    @patch("app.api.v1.health.get_services")
    def test_get_health_db_timeout(self, get_services, app_config):
        # given
        endpoint = "/health"
        self.app.route(endpoint)(health)

        connection = mock_database_connection(get_services)

        mock_config = {"ENVIRONMENT": "production", "VERSION": "4.3.1"}
        connection.command.side_effect = ServerSelectionTimeoutError(
            "Timeout.")
        app_config.get.side_effect = lambda key: mock_config[key]

        # when
        response = self.test_client.get(endpoint)

        # then
        expected = {
            "status": "ok",
            "data": {
                "db": "Timeout.",
                "env": "production",
                "version": "4.3.1"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)

    @patch("app.api.v1.health.get_services")
    def test_get_health_exception(self, get_services):
        # given
        endpoint = "/health"
        self.app.route(endpoint)(health)

        connection = mock_database_connection(get_services)
        connection.command.side_effect = Exception("zero division")

        # when
        with self.assertRaises(Exception) as context:
            self.test_client.get(endpoint)

        # then
        self.assertEqual(str(context.exception), str(
            connection.command.side_effect))
