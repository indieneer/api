import testicles
from app.main import app


class UnitTest(testicles.UnitTest):
    def setUp(self) -> None:
        app.testing = True
        self.app = app.test_client()
        self.app_context = app.app_context
