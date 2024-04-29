from unittest.mock import patch, MagicMock
import json
from app.api.v1.admin.platform_products import get_platform_product_by_id, create_platform_product, delete_platform_product, update_platform_product

from tests import UnitTest
from app.models.platform_products import PlatformProductCreate, PlatformProduct, PlatformProductPatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException


class PlatformProductsTestCase(UnitTest):

    @patch("app.api.v1.admin.platform_products.get_models")
    def test_create_platform_product(self, get_models: MagicMock):
        endpoint = "/platform_products"
        self.app.route(endpoint, methods=["POST"])(create_platform_product)

        create_platform_product_mock = get_models.return_value.platform_products.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_platform_product():
            # given
            mock_platform_product = PlatformProduct(platform_id=1,
                                                    prices=[],
                                                    product_page_url="https://www.example.com/product")
            create_platform_product_mock.return_value = mock_platform_product

            expected_input = PlatformProductCreate(
                platform_id=mock_platform_product.platform_id,
                prices=mock_platform_product.prices,
                product_page_url=mock_platform_product.product_page_url
            )

            expected_response = {
                "status": "ok",
                "data": mock_platform_product.to_json()
            }

            # when
            response = call_api({
                "platform_id": expected_input.platform_id,
                "prices": expected_input.prices,
                "product_page_url": expected_input.product_page_url
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_platform_product_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_platform_product_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"prices": "invalid"})  # Invalid field for simplicity

            # then
            create_platform_product_mock.assert_not_called()

        tests = [
            creates_and_returns_a_platform_product,
            fails_to_create_a_platform_product_when_body_is_invalid
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            create_platform_product_mock.reset_mock()

    @patch("app.api.v1.admin.platform_products.get_models")
    def test_get_platform_product_by_id(self, get_models: MagicMock):
        endpoint = "/admin/platform_products/<string:platform_product_id>"
        self.app.route(endpoint, methods=["GET"])(get_platform_product_by_id)

        get_platform_product_mock = get_models.return_value.platform_products.get

        def call_api(platform_product_id):
            return self.test_client.get(
                endpoint.replace("<string:platform_product_id>", platform_product_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_a_platform_product():
            # given
            mock_platform_product_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_platform_product = PlatformProduct(platform_id=2,
                                                    prices=[],
                                                    product_page_url="https://example.com/test_platform_product_url.png",
                                                    _id=mock_platform_product_id)
            get_platform_product_mock.return_value = mock_platform_product

            expected_response = {
                "status": "ok",
                "data": mock_platform_product.to_json()
            }

            # when
            response = call_api(mock_platform_product_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_platform_product_mock.assert_called_once_with(mock_platform_product_id)

        def does_not_find_a_platform_product_and_returns_an_error():
            # given
            mock_id = "1"
            get_platform_product_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Platform product with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_platform_product_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_platform_product,
            does_not_find_a_platform_product_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_platform_product_mock.reset_mock()

    @patch("app.api.v1.admin.platform_products.get_models")
    def test_update_platform_product(self, get_models: MagicMock):
        endpoint = "/admin/platform_products/<string:platform_product_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_platform_product)

        update_platform_product_mock = get_models.return_value.platform_products.patch

        def call_api(platform_product_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:platform_product_id>", platform_product_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_platform_product():
            # given
            mock_platform_product_id = "507f1f77bcf86cd799439011"
            updated_fields = {"product_page_url": "https://example.com/updated_platform_product_url.png"}
            mock_platform_product = PlatformProduct(platform_id=3,
                                                    prices=[],
                                                    product_page_url="https://example.com/platform_product_url.png"
                                )

            update_platform_product_mock.return_value = mock_platform_product

            expected_response = {
                "status": "ok",
                "data": mock_platform_product.to_json()
            }

            # when
            response = call_api(mock_platform_product_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_platform_product_mock.assert_called_once_with(mock_platform_product_id, PlatformProductPatch(**updated_fields))

        tests = [
            updates_and_returns_the_platform_product,
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            update_platform_product_mock.reset_mock()

    @patch("app.api.v1.admin.platform_products.get_models")
    def test_delete_platform_product(self, get_models: MagicMock):
        endpoint = "/admin/platform_products/<string:platform_product_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_platform_product)

        delete_platform_product_mock = get_models.return_value.platform_products.delete

        def call_api(platform_product_id):
            return self.test_client.delete(
                endpoint.replace("<string:platform_product_id>", platform_product_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_platform_product():
            # given
            mock_platform_product_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Platform product {mock_platform_product_id} successfully deleted"
            }

            # when
            response = call_api(mock_platform_product_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_platform_product_mock.assert_called_once_with(mock_platform_product_id)

        def fails_to_delete_a_nonexistent_platform_product():
            # given
            mock_id = "2"
            delete_platform_product_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Platform product with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_platform_product_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_platform_product,
            fails_to_delete_a_nonexistent_platform_product
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            delete_platform_product_mock.reset_mock()
