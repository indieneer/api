from datetime import datetime, timedelta
from typing import Dict, cast

from dataclasses import dataclass
from app.models import ModelsExtension

from app.services.firebase import FirebaseUserIdentity, FirebaseServiceIdentity


@dataclass
class CacheEntry:
    expires_at: float
    identity: FirebaseUserIdentity | FirebaseServiceIdentity


class LoginsFactory:
    tokens: Dict[str, CacheEntry]
    models: ModelsExtension

    def __init__(self, models: ModelsExtension) -> None:
        self.models = models
        self.tokens = {}

    def create_key(self, email: str, password: str):
        return f"{email}:{password}"

    def cache(self, login: str, password: str, identity: FirebaseUserIdentity | FirebaseServiceIdentity):
        try:
            key = self.create_key(login, password)
            self.tokens[key] = CacheEntry(
                expires_at=(datetime.now() + timedelta(hours=1)).timestamp(),
                identity=identity
            )
        except Exception as e:
            print(f"[Firebase Factory] Failed to cache firebase identity: {e}")

    def login(self, email: str, password: str, cache: bool = True):
        key = self.create_key(email, password)

        identity = None
        if cache:
            data = self.tokens.get(key)

            if data:
                identity = data.identity

        if identity is None:
            identity = self.models.logins.login(email, password)

            if identity is None:
                return

            if cache:
                self.cache(email, password, identity)

        return cast(FirebaseUserIdentity, identity)

    def login_m2m(self, client_id: str, client_secret: str, cache: bool = True):
        key = self.create_key(client_id, client_secret)

        identity = None
        if cache:
            data = self.tokens.get(key)

            if data:
                identity = data.identity

        if identity is None:
            identity = self.models.logins.login_m2m(client_id, client_secret)

            if identity is None:
                return

            if cache:
                self.cache(client_id, client_secret, identity)

        return cast(FirebaseServiceIdentity, identity)
