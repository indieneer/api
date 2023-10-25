from unittest import TestCase

from bson import ObjectId

from app.models.products import ProductCreate
from app.models.profiles import ProfileCreate

from app.models.products import Media, Requirements

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
    LoginsModel, ProductsModel
)

from tests.factory import Factory, ProfilesFactory, ProductsFactory
from tests.fixtures import Fixtures


class IntegrationTest(TestCase):
    DISCOVERY_PATTERN = "test_integration_*.py"

    services: ServicesExtension
    models: ModelsExtension
    factory: Factory
    fixtures: Fixtures

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

        self.strong_password = "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:"
        self.weak_password = "12345678"

        self.services = ServicesExtension(
            auth0=auth0,
            db=db
        )
        self.services.init_app(app)

        self.models = ModelsExtension(
            profiles=ProfilesModel(auth0=auth0, db=db),
            logins=LoginsModel(auth0=auth0),
            products=ProductsModel(db=db),
        )

        self.models.init_app(app)

        self.factory = Factory(
            profiles=ProfilesFactory(
                services=self.services, models=self.models
            ),
            products=ProductsFactory(
                db=db, models=self.models
            )
        )

        self.fixtures = Fixtures(
            regular_user=self.factory.profiles.create(ProfileCreate("test_integration+regular@pork.com", self.strong_password))[0],
            admin_user=self.factory.profiles.create_admin(ProfileCreate("test_integration+admin@pork.com", self.strong_password))[0],
            product=self.factory.products.create(
                ProductCreate(
                    name="Geometry Dash",
                    type="Game",
                    platforms=[
                        "windows",
                        "mac",
                    ],
                    short_description="GD",
                    detailed_description="Geometry dash cool game real",
                    supported_languages=["English"],
                    developers=["RobTop Games"],
                    publishers=["RobTop Games"],
                    genres=[ObjectId("65022c86878d0eb09c1b7dae")],
                    media=Media(
                        background_url="https://example.com",
                        header_url="https://example.com",
                        movies=[
                            {
                                "name": "Trailer",
                                "thumbnail_url": "https://example.com",
                                "formats": {
                                    "webm": {
                                        "480": "https://example.com",
                                        "max": "https://example.com"
                                    },
                                    "mp4": {
                                        "480": "https://example.com",
                                        "max": "https://example.com"
                                    }
                                }
                            }
                        ],
                        screenshots=[
                            {
                                "thumbnail_url": "https://example.com",
                                "full_url": "https://example.com"
                            },
                            {
                                "thumbnail_url": "https://example.com",
                                "full_url": "https://example.com"
                            },
                        ]
                    ).as_json(),
                    release_date="2014-12-22T00:00:00",
                    required_age=0,
                    requirements=Requirements(
                        pc={
                            "minimum": "Avg PC"
                        }
                    ).as_json()
                )
            )[0],
        )
