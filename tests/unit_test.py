from unittest import TestCase

from app import app


class UnitTest(TestCase):
    DISCOVERY_PATTERN = "test_unit_*.py"

    def setUp(self) -> None:
        self.app = app.test_client()
