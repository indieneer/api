from unittest.mock import MagicMock, patch

from app.api.v1.tags import get_tags
from app.models.tags import Tag
from tests import UnitTest


class TagsTestCase(UnitTest):
    @patch("app.api.v1.tags.get_models")
    def test_get_tags(self, get_models: MagicMock):
        endpoint = "/tags"
        self.app.route(endpoint, methods=["GET"])(get_tags)

        get_all_tags_mock = get_models.return_value.tags.get_all

        def call_api():
            return self.test_client.get(endpoint)

        def finds_and_returns_all_tags():
            # given
            mock_tags = [
                Tag(name="tag1"),
                Tag(name="tag2"),
                Tag(name="tag3"),
            ]
            get_all_tags_mock.return_value = mock_tags

            expected_response = {
                "status": "ok",
                "data": [tag.to_json() for tag in mock_tags]
            }

            # when
            response = call_api()

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "application/json")
            get_all_tags_mock.assert_called_once()
