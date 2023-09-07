from flask import Flask
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
import os
from os import environ as env
from api.v1.router import v1_router

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

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
    ENVIRONMENT=env.get("PYTHON_ENV"),
    VERSION="0.0.1",
    AUTH0_DOMAIN=env.get("AUTH0_DOMAIN"),
    AUTH0_AUDIENCE=env.get("AUTH0_AUDIENCE")
)

# blueprint registration
app.register_blueprint(v1_router)

@app.route('/')
def index():
    return 'Hello, Flask!'


if __name__ == '__main__':
    app.run(debug=True)
