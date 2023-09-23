from flask import Flask

from app import (
    configure_app,
    register_routes
)
from config import app_config


app = Flask(__name__)

configure_app(app)
register_routes(app)


if __name__ == '__main__':
    import initializers
    from app.services import (
        Database,
        ManagementAPI,
        ServicesExtension
    )

    # create dependencies
    # todo: add dependency injection for test runs
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

    # run initializers
    initializers.run(services)

    # start the server
    app.run(debug=True, port=app_config["PORT"])
