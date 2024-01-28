from app.services import ManagementAPI
import app.services.firebase
from app.services.firebase import Firebase
from config import app_config
from auth0.authentication import GetToken

from lib.db_utils import Serializable


class AuthenticatedUser(Serializable):
    def __init__(self, identity: app.services.firebase.FirebaseUserIdentity, user: app.services.firebase.FirebaseUser) -> None:
        self.identity = identity
        self.user = user


class LoginsModel:
    auth0: ManagementAPI
    firebase: Firebase
    collection: str = "profiles"

    def __init__(self, auth0: ManagementAPI, firebase: Firebase) -> None:
        self.auth0 = auth0
        self.firebase = firebase

    def login(self, email: str, password: str):
        return self.auth0.auth0_token.login(
            username=email,
            password=password,
            realm='Username-Password-Authentication',
            scope="openid profile email address phone offline_access",
            grant_type="password",
            audience=app_config["AUTH0_AUDIENCE"]
        )

    def login_v2(self, email: str, password: str):
        identity = self.firebase.identity_api.sign_in(email, password)

        return identity

    def login_m2m(self, client_id: str, client_secret: str):
        return GetToken(
            app_config["AUTH0_DOMAIN"],
            client_id,
            client_secret=client_secret
        ).client_credentials(
            grant_type="client_credentials",
            audience=app_config["AUTH0_AUDIENCE"]
        )
