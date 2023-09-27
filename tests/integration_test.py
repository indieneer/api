from unittest import TestCase

from config import app_config
from app.main import app
from app.services import (
    Database,
    ManagementAPI,
    ServicesExtension
)
from app.models import (
    ProfilesModel,
    ModelsExtension,
    LoginsModel
)

from tests.factory import Factory, ProfilesFactory


class IntegrationTest(TestCase):
    DISCOVERY_PATTERN = "test_integration_*.py"

    services: ServicesExtension
    models: ModelsExtension
    factory: Factory

    def setUp(self) -> None:
        app.testing = True
        self.app = app.test_client()

        db = Database(app_config["MONGO_URI"], timeoutMS=3000)
        auth0 = ManagementAPI(
            app_config["AUTH0_DOMAIN"],
            app_config["AUTH0_CLIENT_ID"],
            app_config["AUTH0_CLIENT_SECRET"],
            f'https://{app_config["AUTH0_DOMAIN"]}/api/v2/'
        )

        self.services = ServicesExtension(
            auth0=auth0,
            db=db
        )
        self.services.init_app(app)

        self.models = ModelsExtension(
            profiles=ProfilesModel(auth0=auth0, db=db),
            logins=LoginsModel(auth0=auth0)
        )
        self.models.init_app(app)

        self.factory = Factory(
            profiles=ProfilesFactory(
                services=self.services, models=self.models)
        )
