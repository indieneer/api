from flask import Flask
import testicles
from tests.utils.jwt import MockRequiresAuthExtension


class UnitTest(testicles.UnitTest):
    def setUp(self) -> None:
        self.app = Flask(__name__)

        self.app.testing = True
        self.test_client = self.app.test_client()

        auth_extension = MockRequiresAuthExtension()
        auth_extension.init_app(self.app)