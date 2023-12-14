from unittest import TestCase
import typing
from app.main import app
from app.services import (
    ServicesExtension
)
from app.models import (
    ModelsExtension,
)

from tests.factory import Factory
from tests.fixtures import Fixtures


class IntegrationTest(TestCase):
    DISCOVERY_PATTERN = "test_integration_*.py"

    injected: bool
    services: ServicesExtension
    models: ModelsExtension
    factory: Factory
    fixtures: Fixtures

    def run(self, result: typing.Any | None = None) -> typing.Any | None:
        if self.injected:
            return super().run(result)

        raise Exception("Dependecies must be injected.")

    def inject_dependencies(
        self,
        services: ServicesExtension,
        models: ModelsExtension,
        factory: Factory,
        fixtures: Fixtures
    ):
        self.injected = True
        self.services = services
        self.models = models
        self.factory = factory
        self.fixtures = fixtures

    def setUp(self) -> None:
        app.testing = True
        self.app = app.test_client()
