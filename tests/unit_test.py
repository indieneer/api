from flask import Flask
from app.configure_app import configure_app
import testicles
from tests.utils.jwt import MockRequiresAuthExtension, MockRequiresRoleExtension

class UnitTest(testicles.UnitTest):
    def setUp(self) -> None:
        self.app = Flask(__name__)

        self.app.testing = True
        self.test_client = self.app.test_client()

        auth_extension = MockRequiresAuthExtension()
        auth_extension.init_app(self.app)

        role_extension = MockRequiresRoleExtension()
        role_extension.init_app(self.app)

        configure_app(self.app)