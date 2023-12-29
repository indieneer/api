from app.models.platforms import PlatformsModel, PlatformPatch, PlatformCreate
from tests.integration_test import IntegrationTest
from dataclasses import fields


class PlatformsModelTestCase(IntegrationTest):

    def test_get_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        platform_fixture = self.fixtures.platform

        # when
        retrieved_platform = platforms_model.get(str(platform_fixture._id))

        # then
        self.assertIsNotNone(retrieved_platform)
        self.assertEqual(platform_fixture.name, retrieved_platform.name)

    def test_create_platform(self):
        # given
        platform_fixture = self.fixtures.platform
        create_data = platform_fixture.to_json()
        create_data = {k: create_data[k] for k in [field.name for field in fields(PlatformCreate)]}

        # when
        created_platform = self.models.platforms.create(PlatformCreate(**create_data))
        self.addCleanup(lambda: self.factory.platforms.cleanup(created_platform._id))

        # then
        self.assertIsNotNone(created_platform)
        self.assertEqual(created_platform.name, platform_fixture.name)

    def test_patch_platform(self):
        platforms_model = PlatformsModel(self.services.db)

        # given
        patch_data = PlatformPatch(name="Updated Platform Name")
        fixture = self.fixtures.platform.clone()
        platform_fixture, cleanup = self.factory.platforms.create(fixture)
        self.addCleanup(cleanup)
        # when
        updated_platform = platforms_model.patch(str(platform_fixture._id), patch_data)

        # then
        self.assertIsNotNone(updated_platform)
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
        self.assertIsNotNone(deleted_platform)
        self.assertEqual(deleted_platform.name, platform_fixture.name)
        self.assertIsNone(retrieved_platform_after_deletion)
