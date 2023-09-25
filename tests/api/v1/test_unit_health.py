import unittest
from unittest.mock import patch, Mock
from app import app


class HealthTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    @patch('services.database.Database.client')
    def test_health(self, mock_client):
        mock_db = Mock()
        mock_client.get_default_database.return_value = mock_db

        mock_db.command.side_effect = lambda cmd: {"ok": 1} if cmd == 'ping' else None

        response = self.app.get('/v1/health')

        mock_db.command.assert_called_with('ping')

        self.assertEqual(response.get_json()["data"]["db"], {"ok": 1})
