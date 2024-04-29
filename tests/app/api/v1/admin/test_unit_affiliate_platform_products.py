import datetime
from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.admin.affiliate_platform_products import get_affiliate_platform_product_by_id, create_affiliate_platform_product, delete_affiliate_platform_product, update_affiliate_platform_product
from app.models.affiliates import Affiliate

from app.models.products import Product, Price, Media, Movie, Resolution, Screenshot, Requirements, \
    PlatformOsRequirements, ReleaseDate

from tests import UnitTest
from app.models.affiliate_platform_products import AffiliatePlatformProductCreate, AffiliatePlatformProduct, AffiliatePlatformProductPatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException

# TODO: Create a separate fixtures entity for unit tests
affiliate_platform_product_fixture = AffiliatePlatformProduct(
    affiliate_id="65f9d1648194a472c9f835cd",
    buy_page_url="https://www.example.com",
    prices=[],
    promotions=[],
    platform_product_id="65f9d1648194a472c9f835ce",
    product_id="65f9d1648194a472c9f835cd"
)


class AffiliatePlatformProductsTestCase(UnitTest):

    @patch("app.api.v1.admin.affiliate_platform_products.get_models")
    def test_create_affiliate_platform_product(self, get_models: MagicMock):
        endpoint = "/affiliate_platform_products"
        self.app.route(endpoint, methods=["POST"])(create_affiliate_platform_product)

        create_affiliate_platform_product_mock = get_models.return_value.affiliate_platform_products.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_an_affiliate_platform_product():
            # given
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            create_affiliate_platform_product_mock.return_value = mock_affiliate_platform_product

            expected_input = AffiliatePlatformProductCreate(
                affiliate_id=str(mock_affiliate_platform_product.affiliate_id),
                buy_page_url=mock_affiliate_platform_product.buy_page_url,
                prices=mock_affiliate_platform_product.prices,
                promotions=mock_affiliate_platform_product.promotions,
                platform_product_id=str(mock_affiliate_platform_product.platform_product_id),
                product_id=str(mock_affiliate_platform_product.product_id)
            )

            expected_response = {
                "status": "ok",
                "data": mock_affiliate_platform_product.to_json()
            }

            # when
            response = call_api({
                "affiliate_id": str(expected_input.affiliate_id),
                "buy_page_url": expected_input.buy_page_url,
                "prices": expected_input.prices,
                "promotions": expected_input.promotions,
                "platform_product_id": str(expected_input.platform_product_id),
                "product_id": str(expected_input.product_id)
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_affiliate_platform_product_mock.assert_called_once_with(expected_input)

        def fails_to_create_an_affiliate_platform_product_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"bio": "invalid"})

            # then
            create_affiliate_platform_product_mock.assert_not_called()

        tests = [
            creates_and_returns_an_affiliate_platform_product,
            fails_to_create_an_affiliate_platform_product_when_body_is_invalid
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            create_affiliate_platform_product_mock.reset_mock()

    @patch("app.api.v1.admin.affiliate_platform_products.get_models")
    def test_get_affiliate_platform_product_by_id(self, get_models: MagicMock):
        endpoint = "/admin/affiliate_platform_products/<string:affiliate_platform_product_id>"
        self.app.route(endpoint, methods=["GET"])(get_affiliate_platform_product_by_id)

        get_affiliate_platform_product_mock = get_models.return_value.affiliate_platform_products.get

        def call_api(affiliate_platform_product_id):
            return self.test_client.get(
                endpoint.replace("<string:affiliate_platform_product_id>", affiliate_platform_product_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_an_affiliate_platform_product():
            # given
            mock_affiliate_platform_product_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            get_affiliate_platform_product_mock.return_value = mock_affiliate_platform_product

            expected_response = {
                "status": "ok",
                "data": mock_affiliate_platform_product.to_json()
            }

            # when
            response = call_api(mock_affiliate_platform_product_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_affiliate_platform_product_mock.assert_called_once_with(mock_affiliate_platform_product_id)

        def does_not_find_an_affiliate_platform_product_and_returns_an_error():
            # given
            mock_id = "1"
            get_affiliate_platform_product_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Affiliate platform product with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_affiliate_platform_product_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_an_affiliate_platform_product,
            does_not_find_an_affiliate_platform_product_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_affiliate_platform_product_mock.reset_mock()

    @patch("app.api.v1.admin.affiliate_platform_products.get_models")
    def test_update_affiliate_platform_product(self, get_models: MagicMock):
        endpoint = "/admin/affiliate_platform_products/<string:affiliate_platform_product_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_affiliate_platform_product)

        update_affiliate_platform_product_mock = get_models.return_value.affiliate_platform_products.patch

        def call_api(affiliate_platform_product_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:affiliate_platform_product_id>", affiliate_platform_product_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_affiliate_platform_product():
            # given
            mock_affiliate_platform_product_id = "507f1f77bcf86cd799439011"
            updated_fields = {"buy_page_url": "https://www.example.com/new"}
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            update_affiliate_platform_product_mock.return_value = mock_affiliate_platform_product

            expected_response = {
                "status": "ok",
                "data": mock_affiliate_platform_product.to_json()
            }

            # when
            response = call_api(mock_affiliate_platform_product_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_affiliate_platform_product_mock.assert_called_once_with(mock_affiliate_platform_product_id, AffiliatePlatformProductPatch(**updated_fields))

        tests = [
            updates_and_returns_the_affiliate_platform_product,
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            update_affiliate_platform_product_mock.reset_mock()

    @patch("app.api.v1.admin.affiliate_platform_products.get_models")
    def test_delete_affiliate_platform_product(self, get_models: MagicMock):
        endpoint = "/admin/affiliate_platform_products/<string:affiliate_platform_product_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_affiliate_platform_product)

        delete_affiliate_platform_product_mock = get_models.return_value.affiliate_platform_products.delete

        def call_api(affiliate_platform_product_id):
            return self.test_client.delete(
                endpoint.replace("<string:affiliate_platform_product_id>", affiliate_platform_product_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_affiliate_platform_product():
            # given
            mock_affiliate_platform_product_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Affiliate platform product {mock_affiliate_platform_product_id} successfully deleted"
            }

            # when
            response = call_api(mock_affiliate_platform_product_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_affiliate_platform_product_mock.assert_called_once_with(mock_affiliate_platform_product_id)

        def fails_to_delete_a_nonexistent_affiliate_platform_product():
            # given
            mock_id = "2"
            delete_affiliate_platform_product_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Affiliate platform product with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_affiliate_platform_product_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_affiliate_platform_product,
            fails_to_delete_a_nonexistent_affiliate_platform_product
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            delete_affiliate_platform_product_mock.reset_mock()

