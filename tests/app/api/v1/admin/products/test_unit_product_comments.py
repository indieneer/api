import datetime
from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.admin.products.comments import get_product_comment_by_id, get_all_product_comments, create_product_comment, delete_product_comment, update_product_comment

from tests import UnitTest
from app.models.product_comments import ProductCommentCreate, ProductComment, ProductCommentPatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException

# Using the attached fixture for product comments
product_comment_fixture = ProductComment(
    product_id=str(ObjectId()),
    profile_id=str(ObjectId()),
    text="Nice Game"
)


class ProductCommentsTestCase(UnitTest):

    @patch("app.api.v1.admin.products.comments.get_models")
    def test_create_product_comment(self, get_models: MagicMock):
        endpoint = "/admin/products/product_comments"
        self.app.route(endpoint, methods=["POST"])(create_product_comment)

        create_product_comment_mock = get_models.return_value.product_comments.create

        def call_api(body):
            return self.test_client.post(
                endpoint.replace("<string:product_id>", str(product_comment_fixture.product_id)),
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_product_comment():
            # given
            mock_product_comment = product_comment_fixture.clone()
            create_product_comment_mock.return_value = mock_product_comment

            expected_input = ProductCommentCreate(
                product_id=str(ObjectId),
                profile_id=str(mock_product_comment.profile_id),
                text=mock_product_comment.text
            )

            expected_response = {
                "status": "ok",
                "data": mock_product_comment.to_json()
            }

            # when
            response = call_api({
                "product_id": str(ObjectId),
                "profile_id": str(expected_input.profile_id),
                "text": expected_input.text
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_product_comment_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_product_comment_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"bio": "invalid"})

            # then
            create_product_comment_mock.assert_not_called()

        tests = [
            creates_and_returns_a_product_comment,
            fails_to_create_a_product_comment_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_product_comment_mock.reset_mock)

    @patch("app.api.v1.admin.products.comments.get_models")
    def test_get_product_comment_by_id(self, get_models: MagicMock):
        endpoint = "/admin/products/product_comments/<string:comment_id>"
        self.app.route(endpoint, methods=["GET"])(get_product_comment_by_id)

        get_product_comment_mock = get_models.return_value.product_comments.get

        def call_api(product_id, product_comment_id):
            return self.test_client.get(
                endpoint.replace("<string:product_id>", product_id)
                        .replace("<string:comment_id>", product_comment_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_a_product_comment():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comment_id = str(ObjectId())
            mock_product_comment = product_comment_fixture.clone()
            get_product_comment_mock.return_value = mock_product_comment

            expected_response = {
                "status": "ok",
                "data": mock_product_comment.to_json()
            }

            # when
            response = call_api(mock_product_id, mock_product_comment_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_product_comment_mock.assert_called_once_with(mock_product_comment_id)

        def does_not_find_a_product_comment_and_returns_an_error():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comment_id = str(ObjectId())
            get_product_comment_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Product comment with ID {mock_product_comment_id} not found'
            }

            # when
            response = call_api(mock_product_id, mock_product_comment_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_product_comment_mock.assert_called_once_with(mock_product_comment_id)

        tests = [
            finds_and_returns_a_product_comment,
            does_not_find_a_product_comment_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_product_comment_mock.reset_mock)

    @patch("app.api.v1.admin.products.comments.get_models")
    def test_update_product_comment(self, get_models: MagicMock):
        endpoint = "/admin/products/product_comments/<string:comment_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_product_comment)

        update_product_comment_mock = get_models.return_value.product_comments.patch

        def call_api(product_id, product_comment_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:product_id>", product_id)
                        .replace("<string:comment_id>", product_comment_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_product_comment():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comment_id = str(ObjectId())
            updated_fields = {"text": "Awesome Game"}
            mock_product_comment = product_comment_fixture.clone()
            update_product_comment_mock.return_value = mock_product_comment

            expected_response = {
                "status": "ok",
                "data": mock_product_comment.to_json()
            }

            # when
            response = call_api(mock_product_id, mock_product_comment_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_product_comment_mock.assert_called_once_with(mock_product_comment_id, ProductCommentPatch(**updated_fields))

        tests = [
            updates_and_returns_the_product_comment,
        ]

        self.run_subtests(tests, after_each=update_product_comment_mock.reset_mock)

    @patch("app.api.v1.admin.products.comments.get_models")
    def test_delete_product_comment(self, get_models: MagicMock):
        endpoint = "/admin/products/product_comments/<string:comment_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_product_comment)

        delete_product_comment_mock = get_models.return_value.product_comments.delete

        def call_api(product_id, product_comment_id):
            return self.test_client.delete(
                endpoint.replace("<string:product_id>", product_id)
                        .replace("<string:comment_id>", product_comment_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_product_comment():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comment_id = str(ObjectId())

            expected_response = {
                "message": f"Product comment {mock_product_comment_id} successfully deleted"
            }

            # when
            response = call_api(mock_product_id, mock_product_comment_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_product_comment_mock.assert_called_once_with(mock_product_comment_id)

        def fails_to_delete_a_nonexistent_product_comment():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comment_id = str(ObjectId())
            delete_product_comment_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Product comment with ID {mock_product_comment_id} not found"
            }

            # when
            response = call_api(mock_product_id, mock_product_comment_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_product_comment_mock.assert_called_once_with(mock_product_comment_id)

        tests = [
            deletes_the_product_comment,
            fails_to_delete_a_nonexistent_product_comment
        ]

        self.run_subtests(tests, after_each=delete_product_comment_mock.reset_mock)

    @patch("app.api.v1.admin.products.comments.get_models")
    def test_get_all_product_comments(self, get_models: MagicMock):
        endpoint = "/admin/products/<string:product_id>/comments"
        self.app.route(endpoint, methods=["GET"])(get_all_product_comments)

        get_all_product_comments_mock = get_models.return_value.product_comments.get_all

        def call_api(product_id, limit=None, newest_first=None):
            params = []
            if limit is not None:
                params.append(f"limit={limit}")
            if newest_first is not None:
                params.append(f"newest_first={str(newest_first).lower()}")  # Convert boolean to string
            query_string = "&".join(params)
            full_url = f"{endpoint.replace('<string:product_id>', product_id)}?{query_string}"
            return self.test_client.get(
                full_url,
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def returns_comments_with_limit():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comments = [product_comment_fixture.clone() for _ in range(2)]
            get_all_product_comments_mock.return_value = mock_product_comments[:1]

            expected_response = {
                "status": "ok",
                "data": [comment.to_json() for comment in mock_product_comments[:1]]
            }

            # when
            response = call_api(mock_product_id, limit=1)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_all_product_comments_mock.assert_called_once_with(mock_product_id, limit=1, newest_first=True)

        def returns_comments_with_newest_first_true():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comments = [product_comment_fixture.clone() for _ in range(2)]
            mock_product_comments[0].created_at = datetime.datetime.utcnow()
            mock_product_comments[1].created_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            get_all_product_comments_mock.return_value = mock_product_comments

            expected_response = {
                "status": "ok",
                "data": [comment.to_json() for comment in mock_product_comments]
            }

            # when
            response = call_api(mock_product_id, newest_first=True)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_all_product_comments_mock.assert_called_once_with(mock_product_id, limit=15, newest_first=True)

        def returns_comments_with_newest_first_false():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comments = [product_comment_fixture.clone() for _ in range(2)]
            mock_product_comments[0].created_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            mock_product_comments[1].created_at = datetime.datetime.utcnow()
            get_all_product_comments_mock.return_value = mock_product_comments

            expected_response = {
                "status": "ok",
                "data": [comment.to_json() for comment in mock_product_comments]
            }

            # when
            response = call_api(mock_product_id, newest_first=False)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_all_product_comments_mock.assert_called_once_with(mock_product_id, limit=15, newest_first=False)

        def returns_comments_with_limit_and_newest_first():
            # given
            mock_product_id = str(ObjectId())
            mock_product_comments = [product_comment_fixture.clone() for _ in range(2)]
            mock_product_comments[0].created_at = datetime.datetime.utcnow()
            mock_product_comments[1].created_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            get_all_product_comments_mock.return_value = mock_product_comments[:1]

            expected_response = {
                "status": "ok",
                "data": [comment.to_json() for comment in mock_product_comments[:1]]
            }

            # when
            response = call_api(mock_product_id, limit=1, newest_first=True)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_all_product_comments_mock.assert_called_once_with(mock_product_id, limit=1, newest_first=True)

        tests = [
            returns_comments_with_limit,
            returns_comments_with_newest_first_true,
            returns_comments_with_newest_first_false,
            returns_comments_with_limit_and_newest_first
        ]

        self.run_subtests(tests, after_each=get_all_product_comments_mock.reset_mock)
