

from typing import Dict

from lib.db_utils import Serializable


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


class ExchangeRefreshTokenRequest:
    grant_type: str
    refresh_token: str

    def __init__(self, grant_type: str, /, *, refresh_token: str) -> None:
        super().__init__()

        self.grant_type = grant_type
        self.refresh_token = refresh_token

    def to_json(self):
        return {
            "grant_type": self.grant_type,
            "refresh_token": self.refresh_token
        }
