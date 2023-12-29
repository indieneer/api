from app.models.tags import TagsModel, TagPatch
from tests.integration_test import IntegrationTest

class TagsModelTestCase(IntegrationTest):

    def test_get_tag(self):
        tags_model = TagsModel(self.services.db)

        # given
        tag_fixture = self.fixtures.tag
        created_tag, cleanup = self.factory.tags.create(tag_fixture)
        self.addCleanup(cleanup)

        # when
        retrieved_tag = tags_model.get(str(created_tag._id))

        # then
        if retrieved_tag is None:
            self.assertIsNotNone(retrieved_tag)
        else:
            self.assertEqual(tag_fixture.name, retrieved_tag.name)

    def test_create_tag(self):
        # given
        tag_fixture = self.fixtures.tag

        # when
        created_tag, cleanup = self.factory.tags.create(tag_fixture)
        self.addCleanup(cleanup)

        # then
        if created_tag is None:
            self.assertIsNotNone(created_tag)
        else:
            self.assertEqual(created_tag.name, tag_fixture.name)

    def test_patch_tag(self):
        tags_model = TagsModel(self.services.db)

        # given
        tag_fixture = self.fixtures.tag
        patch_data = TagPatch(name="Updated Name")

        created_tag, cleanup = self.factory.tags.create(tag_fixture)
        self.addCleanup(cleanup)

        # when
        updated_tag = tags_model.patch(str(created_tag._id), patch_data)

        # then
        if updated_tag is None:
            self.assertIsNotNone(updated_tag)
        else:
            self.assertEqual(updated_tag.name, "Updated Name")

    def test_delete_tag(self):
        tags_model = TagsModel(self.services.db)

        # given
        tag_fixture, cleanup = self.factory.tags.create(
            self.fixtures.tag.clone())
        self.addCleanup(cleanup)

        # when
        deleted_tag = tags_model.delete(str(tag_fixture._id))
        retrieved_tag_after_deletion = tags_model.get(str(tag_fixture._id))

        # then
        if deleted_tag is None:
            self.assertIsNotNone(deleted_tag)
        else:
            self.assertEqual(deleted_tag.name, tag_fixture.name)
            self.assertIsNone(retrieved_tag_after_deletion)
