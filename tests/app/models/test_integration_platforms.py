from app.models.platforms import PlatformsModel, PlatformPatch
from tests.integration_test import IntegrationTest


class PlatformsModelTestCase(IntegrationTest):

    def test_get_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        platform_fixture = self.fixtures.platform

        # when
        retrieved_platform = platforms_model.get(str(platform_fixture._id))

        # then
        if retrieved_platform is None:
            self.assertIsNotNone(retrieved_platform)
        else:
            self.assertEqual(platform_fixture._id, retrieved_platform._id)

    def test_patch_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        platform_fixture = self.fixtures.platform
        patch_data = PlatformPatch(name="Updated Platform Name")

        # when
        updated_platform = platforms_model.patch(str(platform_fixture._id), patch_data)

        # then
        if updated_platform is None:
            self.assertIsNotNone(updated_platform)
        else:
            self.assertEqual(updated_platform.name, "Updated Platform Name")

    def test_delete_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        platform_fixture, cleanup = self.factory.platforms.create(
            self.fixtures.platform.clone())
        self.addCleanup(cleanup)

        # when
        deleted_result = platforms_model.delete(str(platform_fixture._id))
        retrieved_platform_after_deletion = platforms_model.get(str(platform_fixture._id))

        # then
        self.assertIsNotNone(deleted_result)
        self.assertIsNone(retrieved_platform_after_deletion)
