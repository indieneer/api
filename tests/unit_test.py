from unittest import TestCase

from app import app


class UnitTest(TestCase):
    def setUp(self) -> None:
        self.app = app.test_client()
