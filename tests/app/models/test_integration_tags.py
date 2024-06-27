from app.models.tags import TagsModel, TagPatch
from tests.integration_test import IntegrationTest


class TagsModelTestCase(IntegrationTest):

    def test_get_tag(self):
        tags_model = self.models.tags

        # given
        tag_fixture = self.fixtures.tag

        # when
        retrieved_tag = tags_model.get(str(tag_fixture._id))

        # then
        self.assertIsNotNone(retrieved_tag)
        self.assertEqual(tag_fixture.name, retrieved_tag.name)

    def test_create_tag(self):
        # given
        tag_fixture = self.fixtures.tag.clone()

        # when
        created_tag = self.models.tags.create(tag_fixture)
        self.addCleanup(lambda: self.factory.tags.cleanup(tag_fixture._id))

        # then
        self.assertIsNotNone(created_tag)
        self.assertEqual(created_tag.name, tag_fixture.name)

    def test_patch_tag(self):
        tags_model = self.models.tags

        # given
        tag_fixture = self.fixtures.tag.clone()
        patch_data = TagPatch(name="Updated Name")

        created_tag, cleanup = self.factory.tags.create(tag_fixture)
        self.addCleanup(cleanup)

        # when
        updated_tag = tags_model.patch(str(created_tag._id), patch_data)

        # then
        self.assertIsNotNone(updated_tag)
        self.assertEqual(updated_tag.name, "Updated Name")

    def test_delete_tag(self):
        tags_model = self.models.tags

        # given
        tag_fixture, cleanup = self.factory.tags.create(
            self.fixtures.tag.clone())
        self.addCleanup(cleanup)

        # when
        deleted_tag = tags_model.delete(str(tag_fixture._id))
        retrieved_tag_after_deletion = tags_model.get(str(tag_fixture._id))

        # then
        self.assertIsNotNone(deleted_tag)
        self.assertEqual(deleted_tag.name, tag_fixture.name)
        self.assertIsNone(retrieved_tag_after_deletion)
