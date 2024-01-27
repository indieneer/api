import json
from typing import Dict
import firebase_admin
from firebase_admin import credentials, auth
import urllib3

from lib.db_utils import Serializable


# Firebase does not provide a library to communicate with the Authentication API
# https://firebase.google.com/docs/reference/rest/auth/#section-sign-in-email-password

class ProviderUserInfo(Serializable):
    def __init__(self, user_info: Dict) -> None:
        self.provider_id = user_info.get("providerId")
        self.federated_id = user_info.get("federatedId")


class FirebaseUser(Serializable):

    def __init__(self, user: Dict) -> None:
        self.local_id = user.get("localId")
        self.email = user.get("email")
        self.display_name = user.get("displayName")
        self.password_hash = user.get("passwordHash")
        self.email_verified = user.get("emailVerified")
        self.password_updated_at = user.get("passwordUpdatedAt")
        self.provider_user_info = [
            ProviderUserInfo(x) for x in user.get("providerUserInfo", [])
        ]
        self.valid_since = user.get("validSince")
        self.disabled = user.get("disabled")
        self.last_login_at = user.get("lastLoginAt")
        self.created_at = user.get("createdAt")
        self.custom_attributes = json.loads(user.get("customAttributes", "{}"))


class FirebaseUserIdentity(Serializable):
    id_token: str
    email: str
    refresh_token: str
    expires_in: str
    local_id: str
    registered: bool

    def __init__(self, identity: Dict) -> None:
        self.id_token = identity.get("idToken", "")
        self.email = identity.get("email", "")
        self.refresh_token = identity.get("refreshToken", "")
        self.expires_in = identity.get("expiresIn", "")
        self.local_id = identity.get("localId", "")
        self.registered = identity.get("registered", False)


class FirebaseIdentityToolkitAPI:
    _base_url: str
    _api_key: str

    def __init__(self, api_key: str) -> None:
        self._base_url = "https://identitytoolkit.googleapis.com"
        self._api_key = api_key

    # TODO: rework
    def sign_in(self, email: str, password: str):
        # https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = urllib3.request(
            "POST", f"{self._base_url}/v1/accounts:signInWithPassword?key={self._api_key}",
            json=payload
        )

        return FirebaseUserIdentity(response.json())

    def lookup(self, idToken: str):
        # https://firebase.google.com/docs/reference/rest/auth#section-get-account-info

        payload = {
            "idToken": idToken
        }

        response = urllib3.request(
            "POST", f"{self._base_url}/v1/accounts:lookup?key={self._api_key}",
            json=payload
        )

        data = response.json()
        user = data.get("users", [])[0]

        return FirebaseUser(user)

    # TODO: refresh token
    # https://firebase.google.com/docs/reference/rest/auth#section-refresh-token

# Firebase Admin SDK
# https://firebase.google.com/docs/reference/admin/python


class Firebase:
    _app: firebase_admin.App
    _api_token: str

    def __init__(self, service_account: str, api_token: str) -> None:
        self._app = self.init_app(service_account)
        self._api_token = api_token

    def init_app(self, service_account: str):
        service_account = json.loads(service_account)
        certificate = credentials.Certificate(service_account)

        return firebase_admin.initialize_app(certificate)

    @property
    def auth(self):
        return auth

    @property
    def identity_api(self):
        return FirebaseIdentityToolkitAPI(self._api_token)
