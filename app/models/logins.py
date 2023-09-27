from app.services import Database, ManagementAPI
from config import app_config


class LoginsModel():
    auth0: ManagementAPI
    collection: str = "profiles"

    def __init__(self, auth0: ManagementAPI) -> None:
        self.auth0 = auth0

    def login(self, email: str, password: str):
        return self.auth0.token.login(
            username=email,
            password=password,
            realm='Username-Password-Authentication',
            scope="openid profile email address phone offline_access",
            grant_type="password",
            audience=app_config["AUTH0_AUDIENCE"]
        )
