from app.services import Database, ManagementAPI
from config import app_config
from auth0.authentication import GetToken

class LoginsModel:
    auth0: ManagementAPI
    collection: str = "profiles"

    def __init__(self, auth0: ManagementAPI) -> None:
        self.auth0 = auth0

    def login(self, email: str, password: str):
        return self.auth0.auth0_token.login(
            username=email,
            password=password,
            realm='Username-Password-Authentication',
            scope="openid profile email address phone offline_access",
            grant_type="password",
            audience=app_config["AUTH0_AUDIENCE"]
        )

    def login_m2m(self, client_id: str, client_secret: str):
        return GetToken(
            app_config["AUTH0_DOMAIN"],
            client_id,
            client_secret=client_secret
        ).client_credentials(
            grant_type="client_credentials",
            audience=app_config["AUTH0_AUDIENCE"]
        )