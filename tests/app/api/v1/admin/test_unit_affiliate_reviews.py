import datetime
from unittest.mock import patch, MagicMock
import json
from app.api.v1.admin.affiliate_reviews import get_affiliate_review_by_id, create_affiliate_review, delete_affiliate_review, update_affiliate_review

from tests import UnitTest
from app.models.affiliate_reviews import AffiliateReviewCreate, AffiliateReview, AffiliateReviewPatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException
from bson import ObjectId


# TODO: Update model dataclass type checking to avoid warnings
class AffiliateReviewsTestCase(UnitTest):

    @patch("app.api.v1.admin.affiliate_reviews.get_models")
    def test_create_affiliate_review(self, get_models: MagicMock):
        endpoint = "/affiliate_reviews"
        self.app.route(endpoint, methods=["POST"])(create_affiliate_review)

        create_affiliate_review_mock = get_models.return_value.affiliate_reviews.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_an_affiliate_review():
            # given
            mock_affiliate_review = AffiliateReview(profile_id=str(ObjectId()),
                                       affiliate_id=str(ObjectId()),
                                       affiliate_platform_product_id=str(ObjectId()),
                                       text="Great product",
                                       rating=5
                                       )
            create_affiliate_review_mock.return_value = mock_affiliate_review

            expected_input = AffiliateReviewCreate(
                profile_id=mock_affiliate_review.profile_id,
                affiliate_id=mock_affiliate_review.affiliate_id,
                affiliate_platform_product_id=mock_affiliate_review.affiliate_platform_product_id,
                text=mock_affiliate_review.text,
                rating=mock_affiliate_review.rating
            )

            expected_response = {
                "status": "ok",
                "data": mock_affiliate_review.to_json()
            }

            # when
            response = call_api({
                "profile_id": str(expected_input.profile_id),
                "affiliate_id": str(expected_input.affiliate_id),
                "affiliate_platform_product_id": str(expected_input.affiliate_platform_product_id),
                "text": expected_input.text,
                "rating": expected_input.rating
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_affiliate_review_mock.assert_called_once_with(expected_input)

        def fails_to_create_an_affiliate_review_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"text": "invalid"})

            # then
            create_affiliate_review_mock.assert_not_called()

        tests = [
            creates_and_returns_an_affiliate_review,
            fails_to_create_an_affiliate_review_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_affiliate_review_mock.reset_mock)

    @patch("app.api.v1.admin.affiliate_reviews.get_models")
    def test_get_affiliate_review_by_id(self, get_models: MagicMock):
        endpoint = "/admin/affiliate_reviews/<string:review_id>"
        self.app.route(endpoint, methods=["GET"])(get_affiliate_review_by_id)

        get_affiliate_review_mock = get_models.return_value.affiliate_reviews.get

        def call_api(affiliate_review_id):
            return self.test_client.get(
                endpoint.replace("<string:review_id>", affiliate_review_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_an_affiliate_review():
            # given
            mock_affiliate_review_id = str(ObjectId())
            mock_affiliate_review = AffiliateReview(profile_id=str(ObjectId()),
                                                    affiliate_id=str(ObjectId()),
                                                    affiliate_platform_product_id=str(ObjectId()),
                                                    text="Very satisfied",
                                                    rating=4,
                                                    _id=mock_affiliate_review_id)
            get_affiliate_review_mock.return_value = mock_affiliate_review

            expected_response = {
                "status": "ok",
                "data": mock_affiliate_review.to_json()
            }

            # when
            response = call_api(mock_affiliate_review_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_affiliate_review_mock.assert_called_once_with(mock_affiliate_review_id)

        def does_not_find_an_affiliate_review_and_returns_an_error():
            # given
            mock_id = "1"
            get_affiliate_review_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Affiliate review with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_affiliate_review_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_an_affiliate_review,
            does_not_find_an_affiliate_review_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_affiliate_review_mock.reset_mock)

    @patch("app.api.v1.admin.affiliate_reviews.get_models")
    def test_update_affiliate_review(self, get_models: MagicMock):
        endpoint = "/admin/affiliate_reviews/<string:review_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_affiliate_review)

        update_affiliate_review_mock = get_models.return_value.affiliate_reviews.patch

        def call_api(affiliate_review_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:review_id>", affiliate_review_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_affiliate_review():
            # given
            mock_affiliate_review_id = str(ObjectId())
            updated_fields = {"text": "Updated review text.", "rating": 3}
            mock_affiliate_review = AffiliateReview(profile_id=str(ObjectId()),
                                                    affiliate_id=str(ObjectId()),
                                                    affiliate_platform_product_id=str(ObjectId()),
                                                    text="Updated review text.",
                                                    rating=3,
                                                    _id=mock_affiliate_review_id
                                                    )

            update_affiliate_review_mock.return_value = mock_affiliate_review

            expected_response = {
                "status": "ok",
                "data": mock_affiliate_review.to_json()
            }

            # when
            response = call_api(mock_affiliate_review_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_affiliate_review_mock.assert_called_once_with(mock_affiliate_review_id, AffiliateReviewPatch(**updated_fields))

        tests = [
            updates_and_returns_the_affiliate_review,
        ]

        self.run_subtests(tests, after_each=update_affiliate_review_mock.reset_mock)

    @patch("app.api.v1.admin.affiliate_reviews.get_models")
    def test_delete_affiliate_review(self, get_models: MagicMock):
        endpoint = "/admin/affiliate_reviews/<string:review_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_affiliate_review)

        delete_affiliate_review_mock = get_models.return_value.affiliate_reviews.delete

        def call_api(affiliate_review_id):
            return self.test_client.delete(
                endpoint.replace("<string:review_id>", affiliate_review_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_affiliate_review():
            # given
            mock_affiliate_review_id = str(ObjectId())

            expected_response = {
                "message": f"Affiliate review {mock_affiliate_review_id} successfully deleted"
            }

            # when
            response = call_api(mock_affiliate_review_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_affiliate_review_mock.assert_called_once_with(mock_affiliate_review_id)

        def fails_to_delete_a_nonexistent_affiliate_review():
            # given
            mock_id = "2"
            delete_affiliate_review_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Affiliate review with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_affiliate_review_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_affiliate_review,
            fails_to_delete_a_nonexistent_affiliate_review
        ]

        self.run_subtests(tests, after_each=delete_affiliate_review_mock.reset_mock)