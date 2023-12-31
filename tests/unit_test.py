import testicles
from app.main import app
from tests.utils.jwt import MockRequiresAuthExtension


class UnitTest(testicles.UnitTest):
    def setUp(self) -> None:
        app.testing = True
        self.app = app.test_client()
        self.app_context = app.app_context

        auth_extension = MockRequiresAuthExtension()
        auth_extension.init_app(app)