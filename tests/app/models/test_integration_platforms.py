from app.models.platforms import PlatformsModel, PlatformPatch
from tests.integration_test import IntegrationTest

class PlatformsModelTestCase(IntegrationTest):

    def test_get_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        platform_fixture = self.fixtures.platform
        created_platform, cleanup = self.factory.platforms.create(platform_fixture)
        self.addCleanup(cleanup)

        # when
        retrieved_platform = platforms_model.get(str(created_platform._id))

        # then
        if retrieved_platform is None:
            self.assertIsNotNone(retrieved_platform)
        else:
            self.assertEqual(platform_fixture.name, retrieved_platform.name)

    def test_create_platform(self):
        # given
        platform_fixture = self.fixtures.platform

        # when
        created_platform, cleanup = self.factory.platforms.create(platform_fixture)
        self.addCleanup(cleanup)

        # then
        if created_platform is None:
            self.assertIsNotNone(created_platform)
        else:
            self.assertEqual(created_platform.name, platform_fixture.name)

    def test_patch_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        platform_fixture = self.fixtures.platform
        patch_data = PlatformPatch(name="Updated Platform Name")

        created_platform, cleanup = self.factory.platforms.create(platform_fixture)
        self.addCleanup(cleanup)

        # when
        updated_platform = platforms_model.patch(str(created_platform._id), patch_data)

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
        deleted_platform = platforms_model.delete(str(platform_fixture._id))
        retrieved_platform_after_deletion = platforms_model.get(str(platform_fixture._id))

        # then
        if deleted_platform is None:
            self.assertIsNotNone(deleted_platform)
        else:
            self.assertEqual(deleted_platform.name, platform_fixture.name)
            self.assertIsNone(retrieved_platform_after_deletion)
