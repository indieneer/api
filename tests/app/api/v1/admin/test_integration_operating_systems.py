import bson
from bson import ObjectId
from app.models.operating_systems import OperatingSystemCreate, OperatingSystemPatch
from tests import IntegrationTest
import lib.constants as constants


class OperatingSystemsTestCase(IntegrationTest):

    # Tests for creation
    def test_create_operating_system(self):
        # given
        operating_system = self.fixtures.operating_system.clone()
        admin_user = self.fixtures.admin_user

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.post(
            "/v1/admin/operating-systems",
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json=operating_system.to_json()
        )

        actual = response.get_json().get("data")

        self.addCleanup(lambda: self.factory.operating_systems.cleanup(
            ObjectId(actual.get("_id"))))

        # then
        expected = operating_system.clone()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected.name, actual.get("name"))

    def test_fails_to_create_an_operating_system_with_invalid_data(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.post(
            f'/v1/admin/operating-systems',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json={"data": "Invalid Data"}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(actual.get("error"), "Invalid data provided.")

    # Tests for getting
    def test_get_operating_system_by_id(self):
        # given
        operating_system = self.fixtures.operating_system
        admin_user = self.fixtures.admin_user

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.get(
            f'/v1/admin/operating-systems/{str(operating_system._id)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        actual = response.get_json().get("data")

        # then
        expected = operating_system.clone()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected.name, actual.get("name"))

    def test_fails_to_get_a_nonexistent_operating_system(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        nonexistent_id = ObjectId()

        # when
        response = self.app.get(
            f'/v1/admin/operating-systems/{nonexistent_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get(
            "error"), f'The operating system with ID {nonexistent_id} was not found.')

    def test_fails_to_get_an_operating_system_by_an_invalid_id(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        invalid_id = "123"

        # when
        response = self.app.get(
            f'/v1/admin/operating-systems/{invalid_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 500)
        # Due to handler exceptions being caught automatically, we cannot use self.assertRaises
        # The error string comes from the bson library and might change when the library updates
        self.assertEqual(actual.get(
            "error"), "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")

    def test_get_operating_systems(self):
        self.skipTest("Fix hardcoded len check")
        # given
        admin_user = self.fixtures.admin_user

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.get(
            f'/v1/admin/operating-systems',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        actual = response.get_json().get("data")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(actual), list)
        self.assertGreater(len(actual), 0)

    # Tests for patching
    def test_update_operating_system(self):
        # given
        os_data = {"name": "Temple OS"}
        update_data = OperatingSystemPatch(name="Updated TempleOS")
        admin_user = self.fixtures.admin_user

        created_os, cleanup = self.factory.operating_systems.create(
            OperatingSystemCreate(**os_data))

        self.addCleanup(cleanup)
        id_to_update = created_os._id

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)
        # when
        response = self.app.patch(
            f'/v1/admin/operating-systems/{str(id_to_update)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json=update_data.to_json()
        )
        actual = response.get_json().get("data")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(actual.get("name"), os_data["name"])
        self.assertEqual(actual.get("name"), update_data.name)

    def test_fails_to_patch_a_nonexistent_operating_system(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        nonexistent_id = ObjectId()

        # when
        response = self.app.patch(
            f'/v1/admin/operating-systems/{nonexistent_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json={"name": "Test Name"}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get("error"), "\"OperatingSystem\" not found.")

    def test_fails_to_patch_an_operating_system_by_an_invalid_id(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        invalid_id = "123"

        # when
        response = self.app.patch(
            f'/v1/admin/operating-systems/{invalid_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json={"name": "Test Name"}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 500)
        # Due to handler exceptions being caught automatically, we cannot use self.assertRaises
        # The error string comes from the bson library and might change when the library updates
        self.assertEqual(actual.get(
            "error"), "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")

    def test_fails_to_patch_an_operating_system_with_invalid_data(self):
        # given
        os_data = {"name": "Temple OS"}
        update_data = {"John Pork": "Loves Pork"}
        admin_user = self.fixtures.admin_user

        created_os, cleanup = self.factory.operating_systems.create(
            OperatingSystemCreate(**os_data))

        self.addCleanup(cleanup)
        id_to_update = created_os._id

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)
        # when
        response = self.app.patch(
            f'/v1/admin/operating-systems/{str(id_to_update)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json=update_data
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 422)
        self.assertEqual(actual.get("error"),
                         "The key \"John Pork\" is not allowed.")

    # Tests for deletion
    def test_delete_operating_system(self):
        # given
        os_data = {"name": "Temple OS"}
        admin_user = self.fixtures.admin_user

        created_os, cleanup = self.factory.operating_systems.create(
            OperatingSystemCreate(**os_data))
        self.addCleanup(cleanup)

        id_to_delete = created_os._id

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)
        # when
        response_delete = self.app.delete(
            f'/v1/admin/operating-systems/{str(id_to_delete)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        response_get = self.app.get(
            f'/v1/admin/operating-systems/{str(id_to_delete)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        deleted_info = response_delete.get_json().get("data").get("deleted_os")
        retrieved_info = response_get.get_json().get("data")

        # then
        self.assertEqual(response_delete.status_code, 200)
        self.assertEqual(deleted_info.get("name"), created_os.name)
        self.assertIsNone(retrieved_info)

    def test_fails_to_delete_a_nonexistent_operating_system(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        nonexistent_id = ObjectId()

        # when
        response = self.app.delete(
            f'/v1/admin/operating-systems/{nonexistent_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get("error"), "\"OperatingSystem\" not found.")

    def test_fails_to_delete_an_operating_system_by_an_invalid_id(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        invalid_id = "123"

        # when
        response = self.app.delete(
            f'/v1/admin/operating-systems/{invalid_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 500)
        # Due to handler exceptions being caught automatically, we cannot use self.assertRaises
        # The error string comes from the bson library and might change when the library updates
        self.assertEqual(actual.get(
            "error"), "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")
