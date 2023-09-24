from flask import Flask
import unittest
from unittest.mock import patch

from app.middlewares import requires_auth, AuthError


class RequiresAuthTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.testing = True

        @self.app.route('/', methods=["GET"])
        @requires_auth
        def handler():
            return "test"

    @patch('app.middlewares.requires_auth.get_token_auth_header')
    def test_incorrect_token(self, get_token_auth_header):
        # given
        get_token_auth_header.side_effect = AuthError(
            {"description": "test error", "code": "invalid_header"}, 401)

        # when
        response = self.app.test_client().get('/')

        # then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "test error")
