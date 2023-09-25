import unittest
from unittest.mock import patch, Mock
from app import app
from bson import ObjectId


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    @patch('services.database.Database.client')
    def test_search(self, mock_client):
        mock_db = Mock()
        mock_db.__getitem__ = Mock()
        mock_client.get_default_database.return_value = mock_db

        params1 = {"page": "1", "name": "Counter"}
        data1 = [
            {
                "_id": ObjectId(),
                "name": "Counter-Strike"
            },
            {
                "_id": ObjectId(),
                "name": "Counter-Strike Global Offensive"
            }
        ]

        meta1 = {
                "total_count": 2,
                "items_on_page": 2,
                "items_per_page": 15,
                "page_count": 1,
                "page": 1
        }

        def aggregate_side_effect(*args):
            directives = args[0]
            num_directives = len(directives)

            if num_directives == 5:
                return data1
            elif num_directives == 2:
                return [{"count": 2}]
            else:
                return []

        mock_db['products'].aggregate.side_effect = aggregate_side_effect

        response = self.app.get('/v1/search', query_string=params1)

        print("DEBUG MESSAGE TEST: ", response)

        self.assertEqual(response.get_json()["data"], data1)
        self.assertEqual(response.get_json()["meta"], meta1)
