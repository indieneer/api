from app.models.tags import Tag, TagCreate
from tests import IntegrationTest


class TagsTestCase(IntegrationTest):
    def test_get_tags(self):
        tags: list[Tag] = []

        # given
        for i in range(5):
            tag, cleanup = self.factory.tags.create(TagCreate(name=f"tag{i}"))
            self.addCleanup(cleanup)
            tags.append(tag)

        # when
        response = self.app.get("/v1/tags")
        json_response = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)

        for tag in tags:
            self.assertIn(tag.to_json(), json_response["data"])
