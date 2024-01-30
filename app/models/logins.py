import app.services.firebase
from app.services.firebase import Firebase

from lib.db_utils import Serializable


class AuthenticatedUser(Serializable):
    def __init__(self, identity: app.services.firebase.FirebaseUserIdentity, user: app.services.firebase.FirebaseUser) -> None:
        self.identity = identity
        self.user = user


class LoginsModel:
    firebase: Firebase
    collection: str = "profiles"

    def __init__(self, firebase: Firebase) -> None:
        self.firebase = firebase

    def login(self, email: str, password: str):
        identity = self.firebase.identity_api.sign_in(email, password)

        return identity

    def exchange_refresh_token(self, refresh_token: str):
        token = self.firebase.secure_token_api.exchange_refresh_token(
            refresh_token
        )

        return token
