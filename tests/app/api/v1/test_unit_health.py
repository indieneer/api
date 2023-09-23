import unittest
from unittest.mock import patch, Mock

from tests import UnitTest
from tests.mocks.services import mock_database_connection


class HealthTestCase(UnitTest):

    @patch("app.api.v1.health.app_config")
    @patch("app.api.v1.health.get_services")
    def test_get_health(self, get_services, app_config):
        # given
        connection = mock_database_connection(get_services)

        mock_config = {"ENVIRONMENT": "production", "VERSION": "4.3.1"}
        connection.command.return_value = {"ok": 1}
        app_config.get.side_effect = lambda key: mock_config[key]

        # when
        response = self.app.get("/v1/health")

        # then
        expected = {
            "status": "ok",
            "data": {
                "db": {"ok": 1},
                "env": "production",
                "version": "4.3.1"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)


if __name__ == "__main__":
    unittest.main()
