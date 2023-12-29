from app.models.logins import LoginsModel
from tests.integration_test import IntegrationTest
import jwt


class LoginsModelTestCase(IntegrationTest):

    def test_login_user(self):
        logins_model = LoginsModel(auth0=self.services.auth0)

        email = "pork@gmail.com"
        password = "126655443"

        result = logins_model.login(email, password)

        access_token = result["access_token"]

        decoded = jwt.decode(access_token, options={"verify_signature": False})

        self.assertIn('https://indieneer.com/profile_id', decoded.keys())
        self.assertNotIn("Admin", decoded['https://indieneer.com/roles'])

    def test_login_admin(self):
        logins_model = LoginsModel(auth0=self.services.auth0)

        email = "john.pork+admin@john.pork"
        password = "JohnPork@1"

        result = logins_model.login(email, password)

        access_token = result["access_token"]

        decoded = jwt.decode(access_token, options={"verify_signature": False})

        self.assertIn('https://indieneer.com/profile_id', decoded.keys())
        self.assertIn("Admin", decoded['https://indieneer.com/roles'])
