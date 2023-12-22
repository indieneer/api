from app.models.operating_systems import OperatingSystemsModel, OperatingSystemPatch
from tests.integration_test import IntegrationTest


class OperatingSystemsModelTestCase(IntegrationTest):

    def test_get_operating_system(self):
        os_model = OperatingSystemsModel(self.services.db)

        # given
        os_fixture = self.fixtures.operating_system

        # when
        retrieved_os = os_model.get(str(os_fixture._id))

        # then
        if retrieved_os is None:
            self.assertIsNotNone(retrieved_os)
        else:
            self.assertEqual(os_fixture._id, retrieved_os._id)

    def test_patch_operating_system(self):
        os_model = OperatingSystemsModel(self.services.db)

        # given
        os_fixture = self.fixtures.operating_system
        patch_data = OperatingSystemPatch(name="Updated OS Name")

        # when
        updated_os = os_model.patch(str(os_fixture._id), patch_data)

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
        deleted_result = os_model.delete(str(os_fixture._id))
        retrieved_os_after_deletion = os_model.get(str(os_fixture._id))

        # then
        self.assertIsNotNone(deleted_result)
        self.assertIsNone(retrieved_os_after_deletion)
