from app.models.tags import TagCreate
from tests import IntegrationTest


class TagsTestCase(IntegrationTest):
    def test_get_tags(self):
        # given
        for i in range(5):
            _, cleanup = self.factory.tags.create(TagCreate(name=f"tag{i}"))
            self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/tags")
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response_json["data"], list)
        self.assertEqual(len(response_json["data"]), 5 + 1)
        self.assertEqual(response_json["data"][1]["name"], "tag0")
