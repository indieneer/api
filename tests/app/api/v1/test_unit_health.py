from unittest.mock import patch

from pymongo.errors import ServerSelectionTimeoutError

from app.api.v1.health import health
from tests import UnitTest


class HealthTestCase(UnitTest):

    @patch("app.api.v1.health.app_config")
    @patch("app.api.v1.health.get_services")
    def test_get_health(self, get_services, app_config):
        endpoint = "/health"
        self.app.route(endpoint)(health)

        connection = get_services.return_value.db.connection

        def call_api():
            return self.test_client.get(endpoint)

        def test_responds_with_200():
            # given
            mock_config = {"ENVIRONMENT": "production", "VERSION": "4.3.1"}
            connection.command.return_value = {"ok": 1}
            app_config.get.side_effect = lambda key: mock_config[key]

            # when
            response = call_api()

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

        def test_returns_timeout_error():
            # given
            mock_config = {"ENVIRONMENT": "production", "VERSION": "4.3.1"}
            connection.command.side_effect = ServerSelectionTimeoutError(
                "Timeout.")
            app_config.get.side_effect = lambda key: mock_config[key]

            # when
            response = call_api()

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

        def test_raises_an_exception():
            # given
            connection.command.side_effect = Exception("zero division")

            # when
            with self.assertRaises(Exception) as context:
                self.test_client.get(endpoint)

            # then
            self.assertEqual(str(context.exception), str(
                connection.command.side_effect))

        tests = [
            test_responds_with_200,
            test_returns_timeout_error,
            test_raises_an_exception
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            connection.reset_mock()
            app_config.reset_mock()
