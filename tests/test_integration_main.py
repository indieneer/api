from typing import Dict

from tests import IntegrationTest

from flask import Flask
from app.main import app, main
from app.services import ServicesExtension
from app.models import ModelsExtension


class MainTestCase(IntegrationTest):

    def test_main_injects_dependencies(self):
        # when
        main()

        # then
        self.assertEqual(type(app), Flask)
        self.assertIsNotNone(app.extensions[ServicesExtension.KEY])
        self.assertIsNotNone(app.extensions[ModelsExtension.KEY])

    def test_main_registers_blueprints(self):
        # then
        self.assertNotEqual(len(app.blueprints.keys()), 0)
