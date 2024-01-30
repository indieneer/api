from datetime import datetime, timedelta
from typing import Dict

from dataclasses import dataclass
from app.models import ModelsExtension

from app.services.firebase import FirebaseUserIdentity


@dataclass
class CacheEntry:
    expires_at: float
    identity: FirebaseUserIdentity


class LoginsFactory:
    tokens: Dict[str, CacheEntry]
    models: ModelsExtension

    def __init__(self, models: ModelsExtension) -> None:
        self.models = models
        self.tokens = {}

    def create_key(self, email: str, password: str):
        return f"{email}:{password}"

    def cache(self, email: str, password: str, identity: FirebaseUserIdentity):
        try:
            key = self.create_key(email, password)
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
            identity = self.models.logins.login_v2(email, password)

            if cache:
                self.cache(email, password, identity)

        return identity
