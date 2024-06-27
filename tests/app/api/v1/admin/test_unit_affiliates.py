import datetime
from unittest.mock import patch, MagicMock
import json
from app.api.v1.admin.affiliates import get_affiliate_by_id, create_affiliate, delete_affiliate, update_affiliate

from tests import UnitTest
from app.models.affiliates import AffiliateCreate, Affiliate, AffiliatePatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException


class AffiliatesTestCase(UnitTest):

    @patch("app.api.v1.admin.affiliates.get_models")
    def test_create_affiliate(self, get_models: MagicMock):
        endpoint = "/affiliates"
        self.app.route(endpoint, methods=["POST"])(create_affiliate)

        create_affiliate_mock = get_models.return_value.affiliates.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_an_affiliate():
            # given
            mock_affiliate = Affiliate(name="John Pork",
                                       slug="john-pork",
                                       became_seller_at=datetime.datetime(2020, 1, 1).isoformat(),
                                       enabled=True,
                                       sales=10,
                                       code="JOHNPORK",
                                       bio="hi",
                                       logo_url="https://www.example.com/"
                                       )
            create_affiliate_mock.return_value = mock_affiliate

            expected_input = AffiliateCreate(
                name=mock_affiliate.name,
                slug=mock_affiliate.slug,
                code=mock_affiliate.code,
                became_seller_at=mock_affiliate.became_seller_at,
                sales=mock_affiliate.sales,
                bio=mock_affiliate.bio,
                enabled=mock_affiliate.enabled,
                logo_url=mock_affiliate.logo_url
            )

            expected_response = {
                "status": "ok",
                "data": mock_affiliate.to_json()
            }

            # when
            response = call_api({
                "name": expected_input.name,
                "slug": expected_input.slug,
                "code": expected_input.code,
                "became_seller_at": expected_input.became_seller_at,
                "sales": expected_input.sales,
                "bio": expected_input.bio,
                "enabled": expected_input.enabled,
                "logo_url": expected_input.logo_url
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_affiliate_mock.assert_called_once_with(expected_input)

        def fails_to_create_an_affiliate_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"bio": "invalid"})

            # then
            create_affiliate_mock.assert_not_called()

        tests = [
            creates_and_returns_an_affiliate,
            fails_to_create_an_affiliate_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_affiliate_mock.reset_mock)

    @patch("app.api.v1.admin.affiliates.get_models")
    def test_get_affiliate_by_id(self, get_models: MagicMock):
        endpoint = "/admin/affiliates/<string:affiliate_id>"
        self.app.route(endpoint, methods=["GET"])(get_affiliate_by_id)

        get_affiliate_mock = get_models.return_value.affiliates.get

        def call_api(affiliate_id):
            return self.test_client.get(
                endpoint.replace("<string:affiliate_id>", affiliate_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_an_affiliate():
            # given
            mock_affiliate_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_affiliate = Affiliate(name="Test Affiliate",
                                       slug="test-affiliate",
                                       became_seller_at=datetime.datetime(2020, 1, 1),
                                       enabled=True,
                                       sales=50,
                                       code="TEST50",
                                       bio="Test affiliate bio.",
                                       logo_url="https://example.com/test_affiliate_logo.png",
                                       _id=mock_affiliate_id)
            get_affiliate_mock.return_value = mock_affiliate

            expected_response = {
                "status": "ok",
                "data": mock_affiliate.to_json()
            }

            # when
            response = call_api(mock_affiliate_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_affiliate_mock.assert_called_once_with(mock_affiliate_id)

        def does_not_find_an_affiliate_and_returns_an_error():
            # given
            mock_id = "1"
            get_affiliate_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Affiliate with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_affiliate_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_an_affiliate,
            does_not_find_an_affiliate_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_affiliate_mock.reset_mock)

    @patch("app.api.v1.admin.affiliates.get_models")
    def test_update_affiliate(self, get_models: MagicMock):
        endpoint = "/admin/affiliates/<string:affiliate_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_affiliate)

        update_affiliate_mock = get_models.return_value.affiliates.patch

        def call_api(affiliate_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:affiliate_id>", affiliate_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_affiliate():
            # given
            mock_affiliate_id = "507f1f77bcf86cd799439011"
            updated_fields = {"bio": "Updated affiliate bio."}
            mock_affiliate = Affiliate(name="John Doe Affiliate",
                                       slug="john-doe-affiliate",
                                       became_seller_at=datetime.datetime(2020, 1, 1),
                                       enabled=True,
                                       sales=100,
                                       code="DOE100",
                                       bio="A top selling affiliate.",
                                       logo_url="https://example.com/john_doe_logo.png"
                                )

            update_affiliate_mock.return_value = mock_affiliate

            expected_response = {
                "status": "ok",
                "data": mock_affiliate.to_json()
            }

            # when
            response = call_api(mock_affiliate_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_affiliate_mock.assert_called_once_with(mock_affiliate_id, AffiliatePatch(**updated_fields))

        tests = [
            updates_and_returns_the_affiliate,
        ]

        self.run_subtests(tests, after_each=update_affiliate_mock.reset_mock)

    @patch("app.api.v1.admin.affiliates.get_models")
    def test_delete_affiliate(self, get_models: MagicMock):
        endpoint = "/admin/affiliates/<string:affiliate_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_affiliate)

        delete_affiliate_mock = get_models.return_value.affiliates.delete

        def call_api(affiliate_id):
            return self.test_client.delete(
                endpoint.replace("<string:affiliate_id>", affiliate_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_affiliate():
            # given
            mock_affiliate_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Affiliate {mock_affiliate_id} successfully deleted"
            }

            # when
            response = call_api(mock_affiliate_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_affiliate_mock.assert_called_once_with(mock_affiliate_id)

        def fails_to_delete_a_nonexistent_affiliate():
            # given
            mock_id = "2"
            delete_affiliate_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Affiliate with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_affiliate_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_affiliate,
            fails_to_delete_a_nonexistent_affiliate
        ]

        self.run_subtests(tests, after_each=delete_affiliate_mock.reset_mock)
