import sys
import os

from bson import ObjectId

from api.v1.profiles import profiles_controller
import unittest
from unittest.mock import patch, Mock
from app import app
from services.database import Database as dbs


class GetProfileTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_profile_found(self):
        test_profile = {"name": "Integration Pork"}
        dbs.client.get_default_database()["profiles"].insert_one(test_profile)

        test_id = test_profile["_id"]

        response = self.app.get(f'/v1/profiles/{test_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["_id"], str(test_id))

        dbs.client.get_default_database()["profiles"].delete_one({"_id": test_id})


    def test_get_profile_not_found(self):
        response = self.app.get('/v1/profiles/64f639f66c078a41dcc0fed9')
        self.assertEqual(response.status_code, 404)

    def test_get_profile_exception(self):
        response = self.app.get('/v1/profiles/64f639f66c078a410fed9')
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()