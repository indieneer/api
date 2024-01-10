from app.middlewares.requires_role import RequiresRoleExtension
import testicles
import typing
from bson import ObjectId

from tests.factory import Factory, ProfilesFactory, ProductsFactory, TagsFactory, PlatformsFactory, \
    OperatingSystemsFactory, BackgroundJobsFactory
from tests.fixtures import Fixtures

from app.models.background_jobs import BackgroundJobsModel, BackgroundJobCreate
from app.models.operating_systems import OperatingSystemCreate
from app.models.platforms import PlatformCreate
from app.models.products import ProductCreate
from app.models.profiles import ProfileCreate
from app.models.tags import TagCreate
from app.models.products import Media, Requirements
from app.models import (
    ProfilesModel,
    PlatformsModel,
    OperatingSystemsModel,
    ModelsExtension,
    LoginsModel,
    ProductsModel,
    TagsModel
)
from app.services import (
    Database,
    ManagementAPI,
    ServicesExtension
)

from app.main import app
from config import app_config
from app.middlewares.requires_auth import RequiresAuthExtension
from app.configure_app import configure_app
from app.register_middlewares import register_middlewares
from app.register_routes import register_routes


class IntegrationTest(testicles.IntegrationTest):
    _test_cases: list[testicles.IntegrationTest] = []
    _cleanup: typing.Union[typing.Callable, None] = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.injected = False
        IntegrationTest._test_cases.append(self)

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

    @staticmethod
    def setUpTestRun():
        print("Initializing integration tests")

        cleanups = []

        try:
            configure_app(app)
            register_routes(app)
            register_middlewares(app)

            db = Database(app_config["MONGO_URI"], timeoutMS=3000)
            auth0 = ManagementAPI(
                app_config["AUTH0_DOMAIN"],
                app_config["AUTH0_CLIENT_ID"],
                app_config["AUTH0_CLIENT_SECRET"],
                f'https://{app_config["AUTH0_DOMAIN"]}/api/v2/'
            )

            # TODO: extract to somewhere to make accessible in tests
            strong_password = "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:"
            weak_password = "12345678"

            services = ServicesExtension(
                auth0=auth0,
                db=db
            )
            services.init_app(app)

            models = ModelsExtension(
                profiles=ProfilesModel(auth0=auth0, db=db),
                platforms=PlatformsModel(db=db),
                operating_systems=OperatingSystemsModel(db=db),
                logins=LoginsModel(auth0=auth0),
                products=ProductsModel(db=db),
                tags=TagsModel(db=db),
                background_jobs=BackgroundJobsModel(db=db)
            )
            models.init_app(app)

            auth_extension = RequiresAuthExtension()
            auth_extension.init_app(app)

            role_extension = RequiresRoleExtension()
            role_extension.init_app(app)

            factory = Factory(
                profiles=ProfilesFactory(
                    services=services, models=models
                ),
                products=ProductsFactory(
                    db=db, models=models
                ),
                tags=TagsFactory(
                    db=db, models=models
                ),
                platforms=PlatformsFactory(
                    db=db, models=models
                ),
                operating_systems=OperatingSystemsFactory(
                    db=db, models=models
                ),
                background_jobs=BackgroundJobsFactory(
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

            tag, cleanup = factory.tags.create(TagCreate(
                "Test tag",
            ))
            cleanups.append(cleanup)

            platform, cleanup = factory.platforms.create(PlatformCreate(
                name="Test Platform",
                base_url="https://www.testplatform.com",
                icon_url="https://www.testplatform.com/icon.ico",
                enabled=True,
            ))
            cleanups.append(cleanup)

            operating_system, cleanup = factory.operating_systems.create(OperatingSystemCreate(
                name="TempleOS"
            ))
            cleanups.append(cleanup)

            background_job, cleanup = factory.background_jobs.create(
                BackgroundJobCreate(
                    type="es_seeder",
                    metadata={
                        "match_query": "test"
                    },
                    created_by="service_test@clients"
                )
            )
            cleanups.append(cleanup)

            fixtures = Fixtures(
                regular_user=regular_user,
                admin_user=admin_user,
                product=product,
                platform=platform,
                operating_system=operating_system,
                tag=tag,
                background_job=background_job
            )

            # Inject dependencies
            for test_case in IntegrationTest._test_cases:
                typing.cast(IntegrationTest, test_case).inject_dependencies(
                    factory=factory,
                    fixtures=fixtures,
                    services=services,
                    models=models
                )
        except Exception as e:
            print(e)

        IntegrationTest._cleanup = lambda: [fixture_cleanup() for fixture_cleanup in cleanups]

    @staticmethod
    def tearDownTestRun():
        if IntegrationTest._cleanup is not None:
            print("Teardown")
            IntegrationTest._cleanup()
