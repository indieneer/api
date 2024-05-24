import datetime
from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.admin.products.replies import get_product_reply_by_id, create_product_reply, delete_product_reply, update_product_reply

from tests import UnitTest
from app.models.product_replies import ProductReplyCreate, ProductReply, ProductReplyPatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException

# Using the attached fixture for product replies
product_reply_fixture = ProductReply(
    comment_id="65f9d1648194a472c9f835cd",
    profile_id="65f9d1648194a472c9f835ce",
    text="Nice Game"
)


class ProductRepliesTestCase(UnitTest):

    @patch("app.api.v1.admin.products.replies.get_models")
    def test_create_product_reply(self, get_models: MagicMock):
        endpoint = "/admin/comments/<string:comment_id>/product_replies"
        self.app.route(endpoint, methods=["POST"])(create_product_reply)

        create_product_reply_mock = get_models.return_value.product_replies.create

        def call_api(body):
            return self.test_client.post(
                endpoint.replace("<string:comment_id>", "65f9d1648194a472c9f835cd"),
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_product_reply():
            # given
            mock_product_reply = product_reply_fixture.clone()
            create_product_reply_mock.return_value = mock_product_reply

            expected_input = ProductReplyCreate(
                comment_id="65f9d1648194a472c9f835cd",
                profile_id=str(mock_product_reply.profile_id),
                text=mock_product_reply.text
            )

            expected_response = {
                "status": "ok",
                "data": mock_product_reply.to_json()
            }

            # when
            response = call_api({
                "profile_id": str(expected_input.profile_id),
                "text": expected_input.text
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_product_reply_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_product_reply_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"bio": "invalid"})

            # then
            create_product_reply_mock.assert_not_called()

        tests = [
            creates_and_returns_a_product_reply,
            fails_to_create_a_product_reply_when_body_is_invalid
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            create_product_reply_mock.reset_mock()

    @patch("app.api.v1.admin.products.replies.get_models")
    def test_get_product_reply_by_id(self, get_models: MagicMock):
        endpoint = "/admin/comments/<string:comment_id>/product_replies/<string:reply_id>"
        self.app.route(endpoint, methods=["GET"])(get_product_reply_by_id)

        get_product_reply_mock = get_models.return_value.product_replies.get

        def call_api(comment_id, product_reply_id):
            return self.test_client.get(
                endpoint.replace("<string:comment_id>", comment_id)
                        .replace("<string:reply_id>", product_reply_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_a_product_reply():
            # given
            mock_comment_id = "65f9d1648194a472c9f835cd"
            mock_product_reply_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_product_reply = product_reply_fixture.clone()
            get_product_reply_mock.return_value = mock_product_reply

            expected_response = {
                "status": "ok",
                "data": mock_product_reply.to_json()
            }

            # when
            response = call_api(mock_comment_id, mock_product_reply_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_product_reply_mock.assert_called_once_with(mock_product_reply_id)

        def does_not_find_a_product_reply_and_returns_an_error():
            # given
            mock_comment_id = "65f9d1648194a472c9f835cd"
            mock_product_reply_id = "1"
            get_product_reply_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Product reply with ID {mock_product_reply_id} not found'
            }

            # when
            response = call_api(mock_comment_id, mock_product_reply_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_product_reply_mock.assert_called_once_with(mock_product_reply_id)

        tests = [
            finds_and_returns_a_product_reply,
            does_not_find_a_product_reply_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_product_reply_mock.reset_mock()

    @patch("app.api.v1.admin.products.replies.get_models")
    def test_update_product_reply(self, get_models: MagicMock):
        endpoint = "/admin/comments/<string:comment_id>/product_replies/<string:reply_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_product_reply)

        update_product_reply_mock = get_models.return_value.product_replies.patch

        def call_api(comment_id, product_reply_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:comment_id>", comment_id)
                        .replace("<string:reply_id>", product_reply_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_product_reply():
            # given
            mock_comment_id = "65f9d1648194a472c9f835cd"
            mock_product_reply_id = "507f1f77bcf86cd799439011"
            updated_fields = {"text": "Awesome Game"}
            mock_product_reply = product_reply_fixture.clone()
            update_product_reply_mock.return_value = mock_product_reply

            expected_response = {
                "status": "ok",
                "data": mock_product_reply.to_json()
            }

            # when
            response = call_api(mock_comment_id, mock_product_reply_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_product_reply_mock.assert_called_once_with(mock_product_reply_id, ProductReplyPatch(**updated_fields))

        tests = [
            updates_and_returns_the_product_reply,
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            update_product_reply_mock.reset_mock()

    @patch("app.api.v1.admin.products.replies.get_models")
    def test_delete_product_reply(self, get_models: MagicMock):
        endpoint = "/admin/comments/<string:comment_id>/product_replies/<string:reply_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_product_reply)

        delete_product_reply_mock = get_models.return_value.product_replies.delete

        def call_api(comment_id, product_reply_id):
            return self.test_client.delete(
                endpoint.replace("<string:comment_id>", comment_id)
                        .replace("<string:reply_id>", product_reply_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_product_reply():
            # given
            mock_comment_id = "65f9d1648194a472c9f835cd"
            mock_product_reply_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Product reply {mock_product_reply_id} successfully deleted"
            }

            # when
            response = call_api(mock_comment_id, mock_product_reply_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_product_reply_mock.assert_called_once_with(mock_product_reply_id)

        def fails_to_delete_a_nonexistent_product_reply():
            # given
            mock_comment_id = "65f9d1648194a472c9f835cd"
            mock_product_reply_id = "2"
            delete_product_reply_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Product reply with ID {mock_product_reply_id} not found"
            }

            # when
            response = call_api(mock_comment_id, mock_product_reply_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_product_reply_mock.assert_called_once_with(mock_product_reply_id)

        tests = [
            deletes_the_product_reply,
            fails_to_delete_a_nonexistent_product_reply
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            delete_product_reply_mock.reset_mock()

