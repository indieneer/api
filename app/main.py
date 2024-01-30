from flask import Flask

from config import app_config

app = Flask(__name__)


def main(app: Flask):
    import initializers
    from app.services import (
        Database,
        Firebase,
        ServicesExtension
    )
    from app.models import (
        ModelsExtension,
        ProfilesModel,
        OperatingSystemsModel,
        ProductsModel,
        LoginsModel,
        TagsModel,
        PlatformsModel,
        BackgroundJobsModel
    )
    from app.middlewares.requires_auth import RequiresAuthExtension
    from app.middlewares.requires_role import RequiresRoleExtension
    from .configure_app import configure_app
    from .register_routes import register_routes
    from .register_middlewares import register_middlewares

    # load config
    configure_app(app)
    register_routes(app)
    register_middlewares(app)

    # create dependencies
    db = Database(app_config["MONGO_URI"], timeoutMS=3000)
    firebase = Firebase(
        app_config["FB_SERVICE_ACCOUNT"], app_config["FB_API_KEY"])

    services = ServicesExtension(
        firebase=firebase,
        db=db
    )
    services.init_app(app)

    models = ModelsExtension(
        profiles=ProfilesModel(db=db, firebase=firebase),
        products=ProductsModel(db=db),
        platforms=PlatformsModel(db=db),
        operating_systems=OperatingSystemsModel(db=db),
        logins=LoginsModel(firebase=firebase),
        tags=TagsModel(db=db),
        background_jobs=BackgroundJobsModel(db=db)
    )
    models.init_app(app)

    auth_extension = RequiresAuthExtension()
    auth_extension.init_app(app)

    role_extension = RequiresRoleExtension()
    role_extension.init_app(app)

    # run initializers
    if app_config.get("ENVIRONMENT", "") in ["staging", "production"]:
        initializers.run(services, models)


if __name__ == "__main__":
    main(app)

    # start the server
    app.run(debug=True, port=app_config["PORT"])
