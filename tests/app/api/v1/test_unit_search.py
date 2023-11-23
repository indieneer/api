from unittest.mock import patch

from bson import ObjectId
from tests.mocks.services import mock_database_connection
from tests import UnitTest


class SearchTestCase(UnitTest):

    @patch('app.api.v1.search.get_services')
    def test_search(self, mock_client):
        mock_client = mock_database_connection(mock_client)

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

        def aggregate_side_effect():
            yield [{
                'items': data1,
                'count': [{"count": 2}]
            }]

        mock_client.__getitem__.return_value.aggregate.side_effect = aggregate_side_effect()

        response = self.app.get('/v1/search', query_string=params1)

        self.assertEqual(response.get_json()["data"], data1)
        self.assertEqual(response.get_json()["meta"], meta1)
