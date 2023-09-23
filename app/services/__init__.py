from flask import Flask

from .auth0 import ManagementAPI
from .database import Database


class ServicesExtension:
    KEY = "services"

    auth0: ManagementAPI
    db: Database

    def __init__(
        self,
        auth0: ManagementAPI,
        db: Database
    ) -> None:
        self.auth0 = auth0
        self.db = db

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self
