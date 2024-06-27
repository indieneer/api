from app.models.operating_systems import OperatingSystemsModel, OperatingSystemPatch, OperatingSystemCreate
from tests.integration_test import IntegrationTest
from dataclasses import fields


class OperatingSystemsModelTestCase(IntegrationTest):

    def test_get_operating_system(self):
        os_model = self.models.operating_systems

        # given
        os_fixture = self.fixtures.operating_system

        # when
        retrieved_os = os_model.get(str(os_fixture._id))

        # then
        self.assertIsNotNone(retrieved_os)
        self.assertEqual(os_fixture.name, retrieved_os.name)

    def test_create_operating_system(self):
        # given
        os_fixture = self.fixtures.platform
        platform_fixture = self.fixtures.platform
        create_data = platform_fixture.to_json()
        create_data = {k: create_data[k] for k in [field.name for field in fields(OperatingSystemCreate)]}

        # when
        created_os = self.models.operating_systems.create(OperatingSystemCreate(**create_data))
        self.addCleanup(lambda: self.factory.operating_systems.cleanup(created_os._id))

        # then
        self.assertIsNotNone(created_os)
        self.assertEqual(created_os.name, os_fixture.name)

    def test_patch_operating_system(self):
        os_model = self.models.operating_systems

        # given
        os_fixture = self.fixtures.operating_system.clone()
        patch_data = OperatingSystemPatch(name="Updated OS Name")

        created_os, cleanup = self.factory.operating_systems.create(os_fixture)
        self.addCleanup(cleanup)

        # when
        updated_os = os_model.patch(str(created_os._id), patch_data)

        # then
        self.assertIsNotNone(updated_os)
        self.assertEqual(updated_os.name, "Updated OS Name")

    def test_delete_operating_system(self):
        os_model = self.models.operating_systems

        # given
        os_fixture, cleanup = self.factory.operating_systems.create(
            self.fixtures.operating_system.clone())
        self.addCleanup(cleanup)

        # when
        deleted_os = os_model.delete(str(os_fixture._id))
        retrieved_os_after_deletion = os_model.get(str(os_fixture._id))

        # then
        self.assertIsNotNone(deleted_os)
        self.assertEqual(deleted_os.name, os_fixture.name)
        self.assertIsNone(retrieved_os_after_deletion)
