from tests import IntegrationTest


class SearchTestCase(IntegrationTest):
    def test_search_by_query(self):
        # given
        product = self.fixtures.product.clone()
        product.name = 'Grand Theft Auto V'
        _, cleanup = self.factory.products.create(product)
        self.addCleanup(cleanup)

        test_cases = [
            {
                "name": "Finds and returns the game when quering by full word",
                "query": "Auto",
                "expect": lambda data: len(data) != 0 and data[0].get("name") == product.name
            },
            {
                "name": "Finds and returns the game when quering by partial word",
                "query": "au",
                "expect": lambda data: len(data) != 0 and data[0].get("name") == product.name
            },
            {
                "name": "Does not find a game",
                "query": "Not existing",
                "expect": lambda data: len(data) == 0
            },
        ]

        # when
        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                response = self.app.get(
                    f'/v1/search?query={test_case["query"]}')
                expect = test_case["expect"]

                # then
                json_data = response.get_json()
                self.assertIsInstance(json_data, dict)
                self.assertIsNone(json_data.get("error"))
                self.assertEquals(response.status_code, 200)

                data = json_data.get("data")

                self.assertTrue(expect(data))
