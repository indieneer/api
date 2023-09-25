from flask import Flask

import unittest

from app.middlewares import get_token_auth_header, AuthError


class RequiresAuthTestCase(unittest.TestCase):

    def test_missing_authorization(self):
        # given
        app = Flask(__name__)
        app.testing = True

        test_cases = [
            {"message": "Authorization header is expected",
                "code": 401, "authorization": None},
            {"message": "Token not found", "code": 401, "authorization": "Bearer"},
            {"message": "Authorization header must start with Bearer",
                "code": 401, "authorization": "NOTBearer a"},
            {"message": "Authorization header must be Bearer token",
                "code": 401, "authorization": "Bearer Bearer Bearer"},
        ]

        for test_case in test_cases:
            # when
            headers = {}
            if test_case["authorization"]:
                headers["Authorization"] = test_case["authorization"]

            with app.test_request_context(
                "/", method="GET", headers=headers
            ):
                with self.assertRaises(AuthError) as e:
                    get_token_auth_header()

                # then
                self.assertEqual(e.exception.status_code, test_case["code"])
                self.assertEqual(
                    e.exception.error["description"], test_case["message"])

    def test_returns_token(self):
        # given
        app = Flask(__name__)
        app.testing = True

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        with app.test_request_context(
            "/", method="GET", headers={"Authorization": f"Bearer {token}"}
        ):
            # when
            extracted = get_token_auth_header()

            # then
            self.assertEqual(extracted, token)
