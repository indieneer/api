
import json
from typing import Dict

from lib.db_utils import Serializable


class ProviderUserInfo(Serializable):
    def __init__(self, user_info: Dict) -> None:
        self.provider_id = user_info.get("providerId")
        self.federated_id = user_info.get("federatedId")


class FirebaseUser(Serializable):

    def __init__(self, **user) -> None:
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

    def __init__(self, **identity) -> None:
        self.id_token = identity.get("idToken", "")
        self.email = identity.get("email", "")
        self.refresh_token = identity.get("refreshToken", "")
        self.expires_in = identity.get("expiresIn", "")
        self.local_id = identity.get("localId", "")
        self.registered = identity.get("registered", False)


class FirebaseCustomIdentity(Serializable):
    id_token: str
    refresh_token: str
    expires_in: str

    def __init__(self, **identity) -> None:
        self.id_token = identity.get("idToken", "")
        self.refresh_token = identity.get("refreshToken", "")
        self.expires_in = identity.get("expiresIn", "")


class SignInWithPasswordRequest:
    email: str
    password: str
    return_secure_token: bool

    def __init__(self, email: str, password: str, /, *, return_secure_token: bool = True) -> None:
        super().__init__()

        self.email = email
        self.password = password
        self.return_secure_token = return_secure_token

    def to_json(self):
        return {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": self.return_secure_token,
        }


class SignInWithCustomTokenRequest:
    token: str
    return_secure_token: bool

    def __init__(self, token: str, /, *, return_secure_token: bool = True) -> None:
        super().__init__()

        self.token = token
        self.return_secure_token = return_secure_token

    def to_json(self):
        return {
            "token": self.token,
            "returnSecureToken": self.return_secure_token,
        }


class LookupRequest:
    id_token: str

    def __init__(self, id_token: str, /) -> None:
        super().__init__()

        self.id_token = id_token

    def to_json(self):
        return {
            "idToken": self.id_token,
        }


class LookupResponse:
    users: list[FirebaseUser]

    def __init__(self, response: dict, /) -> None:
        self.users = [FirebaseUser(**x) for x in response["users"]]
