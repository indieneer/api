from unittest.mock import patch, MagicMock
import json
from app.api.v1.admin.tags import create_tag, delete_tag, get_tag_by_id, update_tag

from tests import UnitTest
from app.models.tags import TagCreate, Tag, TagPatch
from tests.utils.jwt import create_test_token


class TagsTestCase(UnitTest):

    @patch("app.api.v1.admin.tags.get_models")
    def test_create_tag(self, get_models: MagicMock):
        endpoint = "/tags"
        self.app.route(endpoint, methods=["POST"])(create_tag)

        create_tag_mock = get_models.return_value.tags.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_tag():
            # given
            mock_tag = Tag(name="Test tag")
            create_tag_mock.return_value = mock_tag

            expected_input = TagCreate(
                name=mock_tag.name
            )

            expected_response = {
                "status": "ok",
                "data": mock_tag.to_json()
            }

            # when
            response = call_api({
                "name": expected_input.name
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_tag_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_tag_and_returns_an_error():
            # given
            mock_tag = Tag(name="Test tag")
            create_tag_mock.side_effect = Exception("BANG!")

            expected_input = TagCreate(
                name=mock_tag.name
            )

            # when
            with self.assertRaises(Exception) as context:
                call_api({"name": expected_input.name})

            # then
            self.assertEqual(str(context.exception),
                             str(create_tag_mock.side_effect))
            create_tag_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_tag_when_body_is_invalid():
            # when
            with self.assertRaises(Exception) as context:
                call_api({"email": "test@mail.com", })

            # then
            self.assertEqual(str(context.exception), "Bad Request.")
            create_tag_mock.assert_not_called()

        tests = [
            creates_and_returns_a_tag,
            fails_to_create_a_tag_and_returns_an_error,
            fails_to_create_a_tag_when_body_is_invalid
        ]

        self.run_subtests(tests, create_tag_mock.reset_mock)

    @patch("app.api.v1.admin.tags.get_models")
    def test_get_tag(self, get_models: MagicMock):
        endpoint = "/tags/<string:tag_id>"
        self.app.route(endpoint)(get_tag_by_id)

        get_tag_mock = get_models.return_value.tags.get

        def call_api(tag_id):
            return self.test_client.get(
                endpoint.replace("<string:tag_id>", str(tag_id)),
                content_type='application/json',
                headers={
                    "Authorization": "Bearer " + create_test_token("", roles=["admin"])
                }
            )

        def finds_and_returns_a_tag():
            # given
            mock_tag = Tag(name="Test tag")
            get_tag_mock.return_value = mock_tag

            expected_response = {
                "status": "ok",
                "data": mock_tag.to_json()
            }

            # when
            response = call_api(mock_tag._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_tag_mock.assert_called_once_with(str(mock_tag._id))

        def does_not_find_a_tag_and_returns_an_error():
            # given
            mock_id = "1"
            get_tag_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'The tag with ID {mock_id} was not found.'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_tag_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_tag,
            does_not_find_a_tag_and_returns_an_error
        ]

        self.run_subtests(tests, get_tag_mock.reset_mock)

    @patch("app.api.v1.admin.tags.get_models")
    def test_update_tag(self, get_models: MagicMock):
        endpoint = "/tags/<string:tag_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_tag)

        update_tag_mock = get_models.return_value.tags.patch

        def call_api(tag_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:tag_id>", str(tag_id)),
                data=json.dumps(body),
                headers={
                    "Authorization": "Bearer " + create_test_token("", roles=["admin"])
                },
                content_type='application/json'
            )

        def updates_and_returns_the_tag():
            # given
            mock_tag = Tag(name="Test tag")
            update_tag_mock.return_value = mock_tag

            expected_input = TagPatch(
                name=mock_tag.name,
            )
            expected_response = {
                "status": "ok",
                "data": mock_tag.to_json()
            }

            # when
            response = call_api(mock_tag._id, {
                "name": expected_input.name,
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_tag_mock.assert_called_once_with(
                str(mock_tag._id), expected_input)

        tests = [
            updates_and_returns_the_tag
        ]

        self.run_subtests(tests, update_tag_mock.reset_mock)

    @patch("app.api.v1.admin.tags.get_models")
    def test_delete_tag(self, get_models: MagicMock):
        endpoint = "/tags/<string:tag_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_tag)

        delete_tag_mock = get_models.return_value.tags.delete

        def call_api(tag_id):
            return self.test_client.delete(
                endpoint.replace("<string:tag_id>", tag_id),
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_tag():
            # given
            mock_tag = Tag(name="Test tag")
            delete_tag_mock.return_value = mock_tag

            expected_response = {
                "status": "ok",
                "data": f'Successfully deleted the tag with ID {mock_tag._id}'
            }

            # when
            response = call_api(str(mock_tag._id))

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            delete_tag_mock.assert_called_once_with(str(mock_tag._id))

        def fails_to_find_a_tag_and_returns_an_error():
            # given
            mock_id = "1"
            delete_tag_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'The tag with ID {mock_id} was not found.'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_tag_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_tag,
            fails_to_find_a_tag_and_returns_an_error
        ]

        self.run_subtests(tests, delete_tag_mock.reset_mock)
