from flask import Flask
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS

from os import environ as env
from api.v1.router import v1_router
from config import configuration
from services.database import Database as dbs

app = Flask(__name__)

CORS(app, resources={r"/v1/*": {"origins": "*"}})
app.secret_key = env.get("APP_SECRET_KEY")
app.url_map.strict_slashes = False

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

app.config.update(
    **configuration
)

# blueprint registration
app.register_blueprint(v1_router)


@app.route('/')
def index():
    return 'Hello, Flask!'


if __name__ == '__main__':
    from initializers import values  # all the code will be executed

    for value in values:
        value()

    app.run(debug=True, port=configuration["PORT"])
    if not app.testing:
        dbs.initialize()