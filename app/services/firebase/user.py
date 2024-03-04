
import json
from typing import Dict
from lib.db_utils import Serializable


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


class FirebaseRefreshedToken(Serializable):
    expires_in: str
    token_type: str
    refresh_token: str
    id_token: str
    user_id: str
    project_id: str

    def __init__(self, identity: Dict) -> None:
        self.expires_in = identity.get("expires_in", "")
        self.token_type = identity.get("token_type", "")
        self.refresh_token = identity.get("refresh_token", "")
        self.id_token = identity.get("id_token", "")
        self.user_id = identity.get("user_id", "")
        self.project_id = identity.get("project_id", "")


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


class FirebaseServiceIdentity(Serializable):
    id_token: str
    refresh_token: str
    expires_in: str

    def __init__(self, identity: Dict) -> None:
        self.id_token = identity.get("idToken", "")
        self.refresh_token = identity.get("refreshToken", "")
        self.expires_in = identity.get("expiresIn", "")
