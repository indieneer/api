from unittest import TestSuite

from bson import ObjectId

from app.models.background_jobs import BackgroundJobsModel
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
    LoginsModel,
    ProductsModel,
    TagsModel
)

from tests.factory import Factory, ProfilesFactory, ProductsFactory
from tests.fixtures import Fixtures

from tests.integration_test import IntegrationTest


def setup_integration_tests(suite: TestSuite):
    print("Initializing integration tests")

    cleanups = []

    try:
        db = Database(app_config["MONGO_URI"], timeoutMS=3000)
        auth0 = ManagementAPI(
            app_config["AUTH0_DOMAIN"],
            app_config["AUTH0_CLIENT_ID"],
            app_config["AUTH0_CLIENT_SECRET"],
            f'https://{app_config["AUTH0_DOMAIN"]}/api/v2/'
        )

        # TODO: extract to somewhere to make accessable in tests
        strong_password = "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:"
        weak_password = "12345678"

        services = ServicesExtension(
            auth0=auth0,
            db=db
        )
        services.init_app(app)

        models = ModelsExtension(
            profiles=ProfilesModel(auth0=auth0, db=db),
            logins=LoginsModel(auth0=auth0),
            products=ProductsModel(db=db),
            tags=TagsModel(db=db),
            background_jobs=BackgroundJobsModel(db=db)
        )

        models.init_app(app)

        factory = Factory(
            profiles=ProfilesFactory(
                services=services, models=models
            ),
            products=ProductsFactory(
                db=db, models=models
            )
        )

        regular_user, cleanup = factory.profiles.create(ProfileCreate(
            "test_integration+regular@pork.com", strong_password))
        cleanups.append(cleanup)

        admin_user, cleanup = factory.profiles.create_admin(ProfileCreate(
            "test_integration+admin@pork.com", strong_password))
        cleanups.append(cleanup)

        product, cleanup = factory.products.create(
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
                ),
                release_date="2014-12-22T00:00:00",
                required_age=0,
                requirements=Requirements(
                    pc={
                        "minimum": "Avg PC"
                    }
                )
            )
        )
        cleanups.append(cleanup)

        fixtures = Fixtures(
            regular_user=regular_user,
            admin_user=admin_user,
            product=product,
        )

        # Inject dependencies

        def inject_recursively(suite: TestSuite):
            for test_case in suite:
                if isinstance(test_case, TestSuite):
                    inject_recursively(test_case)
                elif isinstance(test_case, IntegrationTest):
                    test_case.inject_dependencies(
                        factory=factory,
                        fixtures=fixtures,
                        services=services,
                        models=models
                    )

        inject_recursively(suite)
    except Exception as e:
        print(e)

    return lambda: [cleanup() for cleanup in cleanups]
