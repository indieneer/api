import traceback
import typing

from bson import ObjectId

import lib.constants as constants
import testicles
from app.configure_app import configure_app
from app.main import app
from app.middlewares.requires_auth import RequiresAuthExtension
from app.middlewares.requires_role import RequiresRoleExtension
from app.models import (LoginsModel, ModelsExtension, OperatingSystemsModel,
                        PlatformsModel, ProductsModel, ProfilesModel,
                        ServiceProfilesModel, TagsModel)
from app.models.background_jobs import BackgroundJobCreate, BackgroundJobsModel
from app.models.operating_systems import OperatingSystemCreate
from app.models.platforms import PlatformCreate
from app.models.products import Media, ProductCreate, Requirements
from app.models.profiles import ProfileCreate
from app.models.service_profiles import ServiceProfileCreate
from app.models.tags import TagCreate
from app.register_middlewares import register_middlewares
from app.register_routes import register_routes
from app.services import Database, Firebase, ServicesExtension
from config import app_config
from config.constants import FirebaseRole
from tests.factory import (BackgroundJobsFactory, Factory, LoginsFactory,
                           OperatingSystemsFactory, PlatformsFactory,
                           ProductsFactory, ProfilesFactory,
                           ServiceProfilesFactory, TagsFactory)
from tests.fixtures import Fixtures


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

    def before_all(self):
        """Hook function to set up test run for a class
        """
        pass

    def run_subtests(self,
                     tests: list[typing.Callable],
                     before_each: typing.Callable | None = None,
                     before_all: typing.Callable | None = None,
                     after_each: typing.Callable | None = None,
                     after_all: typing.Callable | None = None,
                     ):
        if before_all:
            before_all()

        for test in tests:
            if before_each:
                before_each()

            with self.subTest(test.__name__):
                test()

            if after_each:
                after_each()

        if after_all:
            after_all()

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
            firebase = Firebase(
                app_config["FB_SERVICE_ACCOUNT"], app_config["FB_API_KEY"])

            strong_password = constants.strong_password
            weak_password = constants.weak_password

            services = ServicesExtension(
                firebase=firebase,
                db=db
            )
            services.init_app(app)

            profiles_model = ProfilesModel(firebase=firebase, db=db)
            service_profiles_model = ServiceProfilesModel(
                firebase=firebase, db=db)
            models = ModelsExtension(
                profiles=profiles_model,
                platforms=PlatformsModel(db=db),
                operating_systems=OperatingSystemsModel(db=db),
                logins=LoginsModel(
                    firebase=firebase,
                    profiles=profiles_model,
                    service_profiles=service_profiles_model
                ),
                products=ProductsModel(db=db),
                tags=TagsModel(db=db),
                background_jobs=BackgroundJobsModel(db=db),
                service_profiles=service_profiles_model
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
                ),
                logins=LoginsFactory(
                    models=models
                ),
                service_profiles=ServiceProfilesFactory(
                    models=models,
                    services=services
                )
            )

            regular_user, cleanup = factory.profiles.create(ProfileCreate(
                email="test_integration+regular@pork.com",
                password=strong_password,
                nickname="test_integration_regular",
            ))
            cleanups.append(cleanup)

            admin_user, cleanup = factory.profiles.create(ProfileCreate(
                email="test_integration+admin@pork.com",
                password=strong_password,
                nickname="test_integration_admin",
                role=FirebaseRole.Admin
            ))
            cleanups.append(cleanup)

            service_profile, cleanup = factory.service_profiles.create(ServiceProfileCreate(
                permissions=[]
            ))
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
                    created_by=str(service_profile._id)
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
                background_job=background_job,
                service_profile=service_profile
            )

            # Inject dependencies and trigger before all
            for test_case in IntegrationTest._test_cases:
                typing.cast(IntegrationTest, test_case).inject_dependencies(
                    factory=factory,
                    fixtures=fixtures,
                    services=services,
                    models=models
                )
                typing.cast(IntegrationTest, test_case).before_all()
        except Exception as e:
            raise e

        def cleanup():
            for fixture_cleanup in cleanups:
                try:
                    fixture_cleanup()
                except Exception as e:
                    print(f"Failed to cleanup a fixture: {str(e)}")

        IntegrationTest._cleanup = cleanup

    @staticmethod
    def tearDownTestRun():
        if IntegrationTest._cleanup is not None:
            print("Teardown")
            IntegrationTest._cleanup()
