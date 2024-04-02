from tests import IntegrationTest


class ProductsTestCase(IntegrationTest):
    def test_get_product_by_slug(self):
        # when
        response = self.app.get(
            f'/v1/products/geometry-dash'
        )

        actual = response.get_json().get("data")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual.get("name"), "Geometry Dash")

    def test_fails_to_get_a_nonexistent_product(self):
        # when
        response = self.app.get(
            f'/v1/products/this-will-never-exist-hj43hj32b3wejfdns'
        )

        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get("error"), "\"Product\" not found.")
