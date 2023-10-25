from unittest import TestCase
from app.main import app


class UnitTest(TestCase):
    DISCOVERY_PATTERN = "test_unit_*.py"

    def setUp(self) -> None:
        app.testing = True
        self.app = app.test_client()
