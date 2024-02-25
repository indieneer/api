from unittest.mock import patch

from bson import ObjectId

from app.api.v1.search import search
from tests import UnitTest


class SearchTestCase(UnitTest):

    @patch('app.api.v1.search.get_services')
    def test_search(self, get_services):
        # given
        endpoint = "/search"
        self.app.route(endpoint)(search)

        mock_client = get_services.return_value.db.connection

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

        # when
        response = self.test_client.get(endpoint, query_string=params1)

        # then
        self.assertEqual(response.get_json()["data"], data1)
        self.assertEqual(response.get_json()["meta"], meta1)
