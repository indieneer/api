from datetime import datetime, timedelta
import json
from typing import Dict
from app.models import ModelsExtension
from app.models.logins import LoginsModel
from os import environ as env, path
import os


class LoginsFactory:
    cache_path: str
    tokens: Dict[str, Dict]
    model: LoginsModel

    def __init__(self, models: ModelsExtension) -> None:
        self.models = models
        self.cache_dir = env.get("AUTH0_CACHE_DIR") or ""
        self.cache_path = path.join(self.cache_dir, "tokens")

        self.restore_cache()

    def purge_cache(self):
        now = datetime.now().timestamp()

        for key, data in self.tokens.items():
            expires_at = data.get("expires_at") or 0
            if now >= expires_at:
                del self.tokens[key]

    def ensure_cache_exists(self):
        os.makedirs(self.cache_dir, exist_ok=True)

    def create_key(self, email: str, password: str):
        return f"{email}:{password}"

    def restore_cache(self):
        try:
            self.ensure_cache_exists()

            with open(self.cache_path, "r") as file:
                self.tokens = json.load(file) or {}
                self.purge_cache()
        except Exception as e:
            self.tokens = {}
            print(
                f"[Auth0 Factory] Failed to restore cache for auth0 tokens: {e}")

    def cache(self, email: str, password: str, identity: Dict):
        try:
            self.ensure_cache_exists()

            key = self.create_key(email, password)
            self.tokens[key] = {
                "expires_at": (datetime.now() + timedelta(hours=23)).timestamp(), "identity": identity}

            with open(self.cache_path, "w+") as file:
                json.dump(self.tokens, file)
        except Exception as e:
            print(f"[Auth0 Factory] Failed to cache auth0 tokens: {e}")

    def login(self, email: str, password: str, cache: bool = True):
        key = self.create_key(email, password)

        identity = None
        if cache:
            data = self.tokens.get(key)

            if data:
                identity = data["identity"]

                print(f"[Auth0 Factory] Using cache for {email}")

        if identity is None:
            identity = self.models.logins.login(email, password)

            if cache:
                self.cache(email, password, identity)

        return identity
