from app.models.operating_systems import OperatingSystemsModel, OperatingSystemPatch
from tests.integration_test import IntegrationTest


class OperatingSystemsModelTestCase(IntegrationTest):

    def test_get_operating_system(self):
        os_model = OperatingSystemsModel(self.services.db)

        # given
        os_fixture = self.fixtures.operating_system
        created_os, cleanup = self.factory.operating_systems.create(os_fixture)
        self.addCleanup(cleanup)

        # when
        retrieved_os = os_model.get(str(created_os._id))

        # then
        if retrieved_os is None:
            self.assertIsNotNone(retrieved_os)
        else:
            self.assertEqual(os_fixture.name, retrieved_os.name)

    def test_create_operating_system(self):
        # given
        os_fixture = self.fixtures.operating_system

        # when
        created_os, cleanup = self.factory.operating_systems.create(os_fixture)
        self.addCleanup(cleanup)

        # then
        if created_os is None:
            self.assertIsNotNone(created_os)
        else:
            self.assertEqual(created_os.name, os_fixture.name)

    def test_patch_operating_system(self):
        os_model = OperatingSystemsModel(self.services.db)

        # given
        os_fixture = self.fixtures.operating_system
        patch_data = OperatingSystemPatch(name="Updated OS Name")

        created_os, cleanup = self.factory.operating_systems.create(os_fixture)
        self.addCleanup(cleanup)

        # when
        updated_os = os_model.patch(str(created_os._id), patch_data)

        # then
        if updated_os is None:
            self.assertIsNotNone(updated_os)
        else:
            self.assertEqual(updated_os.name, "Updated OS Name")

    def test_delete_operating_system(self):
        os_model = OperatingSystemsModel(self.services.db)

        # given
        os_fixture, cleanup = self.factory.operating_systems.create(
            self.fixtures.operating_system.clone())
        self.addCleanup(cleanup)

        # when
        deleted_os = os_model.delete(str(os_fixture._id))
        retrieved_os_after_deletion = os_model.get(str(os_fixture._id))

        # then
        if deleted_os is None:
            self.assertIsNotNone(deleted_os)
        else:
            self.assertEqual(deleted_os.name, os_fixture.name)
            self.assertIsNone(retrieved_os_after_deletion)
