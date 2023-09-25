from bson import ObjectId
import unittest
from unittest.mock import patch, Mock
from app import app


class GetProfileTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    @patch('services.database.Database.client')
    def test_get_profile_found(self, mock_client):
        mock_db = Mock()
        mock_db.__getitem__ = Mock()
        mock_collection = Mock()
        profile_data = {'_id': ObjectId('5f50e045d48d371f9b985e1e'), 'name': 'John'}

        mock_collection.find_one.return_value = profile_data
        mock_db.__getitem__.return_value = mock_collection
        mock_client.get_default_database.return_value = mock_db

        response = self.app.get('/v1/profiles/5f50e045d48d371f9b985e1e')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], {'_id': '5f50e045d48d371f9b985e1e', 'name': 'John'})

    @patch('services.database.Database.client')
    def test_get_profile_not_found(self, mock_client):
        mock_db = Mock()
        mock_db.__getitem__ = Mock()
        mock_collection = Mock()

        mock_collection.find_one.return_value = None
        mock_db.__getitem__.return_value = mock_collection
        mock_client.get_default_database.return_value = mock_db

        response = self.app.get('/v1/profiles/5f50e045d48d371f9b985e1e')

        self.assertEqual(response.status_code, 404)

    @patch('services.database.Database.client')
    def test_get_profile_exception(self, mock_client):
        mock_client.get_default_database.side_effect = Exception("Database error")

        response = self.app.get('/v1/profiles/5f50e045d48d371f9b985e1e')
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
