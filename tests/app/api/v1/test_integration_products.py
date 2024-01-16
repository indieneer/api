import bson
from bson import ObjectId
from tests import IntegrationTest


class ProductsTestCase(IntegrationTest):

    # Tests for getting
    def test_get_product_by_slug(self):
        # given
        regular_user = self.fixtures.regular_user

        tokens = self.models.logins.login(regular_user.email, "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")

        # when
        response = self.app.get(
            # TODO: Replace with a proper fixture later
            f'/v1/products/test-geometry-dash',
            headers={"Authorization": f'Bearer {tokens["access_token"]}'}
        )

        actual = response.get_json()
        print(actual)

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual.get("name"), "Updated Name")

    def test_fails_to_get_a_nonexistent_product(self):
        # given
        regular_user = self.fixtures.regular_user

        tokens = self.models.logins.login(regular_user.email, "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")

        # when
        response = self.app.get(
            f'/v1/products/this-will-never-exist-hj43hj32b3wejfdns',
            headers={"Authorization": f'Bearer {tokens["access_token"]}'}
        )

        actual = response.get_json().get("data")

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get("error"), "Abc")