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

    def test_main_registers_error_handler(self):
        # then
        error_handlers = app.error_handler_spec

        def recursively_find(d: Dict):
            for key in d:
                if key == Exception:
                    return True
                elif isinstance(d[key], dict):
                    if recursively_find(d[key]):
                        return True

            return False

        unhandled_exception_handler = recursively_find(error_handlers)
        self.assertTrue(unhandled_exception_handler)
