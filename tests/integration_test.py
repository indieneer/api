from unittest import TestCase

from config import app_config
from app.main import app
from app.services import (
    Database,
    ManagementAPI,
    ServicesExtension
)


class IntegrationTest(TestCase):
    DISCOVERY_PATTERN = "test_integration_*.py"

    def setUp(self) -> None:
        app.testing = True
        self.app = app.test_client()

        db = Database(app_config["MONGO_URI"], timeoutMS=3000)
        auth0 = ManagementAPI(
            app_config["AUTH0_DOMAIN"],
            app_config["AUTH0_CLIENT_ID"],
            app_config["AUTH0_CLIENT_SECRET"],
            app_config["AUTH0_AUDIENCE"]
        )

        services = ServicesExtension(
            auth0=auth0,
            db=db
        )
        services.init_app(app)
