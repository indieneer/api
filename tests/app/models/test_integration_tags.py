from app.models.tags import TagsModel, TagPatch
from tests.integration_test import IntegrationTest


class TagsModelTestCase(IntegrationTest):

    def test_get_tag(self):
        tags_model = TagsModel(self.services.db)

        # given
        tag = self.fixtures.tag

        # when
        retrieved_tag = tags_model.get(str(tag._id))

        # then
        if retrieved_tag is None:
            self.assertIsNotNone(retrieved_tag)
        else:
            self.assertEqual(tag._id, retrieved_tag._id)

    def test_patch_tag(self):
        tags_model = TagsModel(self.services.db)

        # given
        tag = self.fixtures.tag
        patch_data = TagPatch(name="Updated Name")

        # when
        updated_tag = tags_model.patch(str(tag._id), patch_data)

        # then
        if updated_tag is None:
            self.assertIsNotNone(updated_tag)
        else:
            self.assertEqual(updated_tag.name, "Updated Name")

    def test_delete_tag(self):
        tags_model = TagsModel(self.services.db)
        # given
        tag, cleanup = self.factory.tags.create(
            self.fixtures.tag.clone())
        self.addCleanup(cleanup)

        # when
        deleted_result = tags_model.delete(str(tag._id))
        retrieved_tag_after_deletion = tags_model.get(str(tag._id))

        # then
        self.assertIsNotNone(deleted_result)
        self.assertIsNone(retrieved_tag_after_deletion)
