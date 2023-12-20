from flask import Flask
from .configure_app import configure_app
from .register_routes import register_routes
from .register_middlewares import register_middlewares
from config import app_config

app = Flask(__name__)

configure_app(app)
register_routes(app)
register_middlewares(app)


def main():
    import initializers
    from app.services import (
        Database,
        ManagementAPI,
        ServicesExtension
    )
    from app.models import (
        ModelsExtension,
        ProfilesModel,
        ProductsModel,
        LoginsModel,
        TagsModel,
        PlatformsModel,
        PlatformsOSModel,
        BackgroundJobsModel
    )

    # create dependencies
    # TODO: add dependency injection for test runs
    db = Database(app_config["MONGO_URI"], timeoutMS=3000)
    auth0 = ManagementAPI(
        app_config["AUTH0_DOMAIN"],
        app_config["AUTH0_CLIENT_ID"],
        app_config["AUTH0_CLIENT_SECRET"],
        'https://{}/api/v2/'.format(app_config["AUTH0_DOMAIN"])
    )

    services = ServicesExtension(
        auth0=auth0,
        db=db
    )
    services.init_app(app)

    models = ModelsExtension(
        profiles=ProfilesModel(db=db, auth0=auth0),
        products=ProductsModel(db=db),
        platforms=PlatformsModel(db=db),
        platforms_os=PlatformsOSModel(db=db),
        logins=LoginsModel(auth0=auth0),
        tags=TagsModel(db=db),
        background_jobs=BackgroundJobsModel(db=db)
    )
    models.init_app(app)

    # run initializers

    if app_config.get("ENVIRONMENT", "") in ["staging", "production"]:
        initializers.run(services)


if __name__ == "__main__":
    main()

    # start the server
    app.run(debug=True, port=app_config["PORT"])
