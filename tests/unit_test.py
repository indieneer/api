import typing

from flask import Flask

import testicles
from app.configure_app import configure_app
from tests.utils.jwt import (MockRequiresAuthExtension,
                             MockRequiresRoleExtension)


class UnitTest(testicles.UnitTest):
    def setUp(self) -> None:
        self.app = Flask(__name__)

        self.app.testing = True
        self.test_client = self.app.test_client()

        auth_extension = MockRequiresAuthExtension()
        auth_extension.init_app(self.app)

        role_extension = MockRequiresRoleExtension()
        role_extension.init_app(self.app)

        configure_app(self.app)

    def run_subtests(self,
                     tests: list[typing.Callable],
                     before_each: typing.Callable | None = None,
                     before_all: typing.Callable | None = None,
                     after_each: typing.Callable | None = None,
                     after_all: typing.Callable | None = None,
                     ):
        if before_all:
            before_all()

        for test in tests:
            if before_each:
                before_each()

            with self.subTest(test.__name__):
                test()

            if after_each:
                after_each()

        if after_all:
            after_all()
