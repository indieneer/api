from bson import ObjectId
from app.models.platforms import PlatformCreate, PlatformPatch
from tests import IntegrationTest
import lib.constants as constants


class PlatformsTestCase(IntegrationTest):

    # Tests for creation
    def test_create_platform(self):
        # given
        platform_data = {
            "name": "Test Platform",
            "base_url": "www.test-platform.com/",
            "icon_url": "www.test-platform.com/icon",
            "enabled": True
        }
        platform = PlatformCreate(**platform_data)
        admin_user = self.fixtures.admin_user

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.post(
            "/v1/admin/platforms",
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json=platform.to_json()
        )

        actual = response.get_json().get("data")

        self.addCleanup(lambda: self.factory.platforms.cleanup(
            ObjectId(actual.get("_id"))))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(platform.name, actual.get("name"))

    def test_fails_to_create_a_platform_with_invalid_data(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.post(
            f'/v1/admin/platforms',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json={"data": "Invalid Data"}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(actual.get("error"), "Invalid data provided.")

    # Tests for getting
    def test_get_platform_by_id(self):
        # given
        platform = self.fixtures.platform
        admin_user = self.fixtures.admin_user

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.get(
            f'/v1/admin/platforms/{str(platform._id)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        actual = response.get_json().get("data")

        # then
        expected = platform.clone()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected.name, actual.get("name"))

    def test_fails_to_get_a_nonexistent_platform(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        nonexistent_id = ObjectId()

        # when
        response = self.app.get(
            f'/v1/admin/platforms/{nonexistent_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get(
            "error"), f'The platform with ID {nonexistent_id} was not found.')

    def test_fails_to_get_a_platform_by_an_invalid_id(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        invalid_id = "123"

        # when
        response = self.app.get(
            f'/v1/admin/platforms/{invalid_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(actual.get("error"),
                         "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")

    def test_get_platforms(self):
        # given
        admin_user = self.fixtures.admin_user

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        # when
        response = self.app.get(
            f'/v1/admin/platforms',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        actual = response.get_json().get("data")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(actual), list)
        self.assertGreater(len(actual), 0)

    # Tests for updating
    def test_update_platform(self):
        # given
        platform_data = {
            "name": "Test Platform",
            "base_url": "www.test-platform.com/",
            "icon_url": "www.test-platform.com/icon",
            "enabled": True
        }
        update_data = PlatformPatch(name="Updated Test Platform")
        admin_user = self.fixtures.admin_user

        created_platform, cleanup = self.factory.platforms.create(
            PlatformCreate(**platform_data))

        self.addCleanup(cleanup)
        id_to_update = created_platform._id

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)
        # when
        response = self.app.patch(
            f'/v1/admin/platforms/{str(id_to_update)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json=update_data.to_json()
        )
        actual = response.get_json().get("data")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(actual.get("name"), platform_data["name"])
        self.assertEqual(actual.get("name"), update_data.name)

    def test_fails_to_patch_a_nonexistent_platform(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        nonexistent_id = ObjectId()

        # when
        response = self.app.patch(
            f'/v1/admin/platforms/{nonexistent_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json={"name": "Test Name"}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get("error"), "\"Platform\" not found.")

    def test_fails_to_patch_a_platform_by_an_invalid_id(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        invalid_id = "123"

        # when
        response = self.app.patch(
            f'/v1/admin/platforms/{invalid_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json={"name": "Test Name"}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(actual.get("error"),
                         "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")

    def test_fails_to_patch_a_platform_with_invalid_data(self):
        # given
        platform_data = {
            "name": "Test Platform",
            "base_url": "www.test-platform.com/",
            "icon_url": "www.test-platform.com/icon",
            "enabled": True
        }
        update_data = {"John Pork": "Loves Pork"}
        admin_user = self.fixtures.admin_user

        created_platform, cleanup = self.factory.platforms.create(
            PlatformCreate(**platform_data))

        self.addCleanup(cleanup)
        id_to_update = created_platform._id

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)
        # when
        response = self.app.patch(
            f'/v1/admin/platforms/{str(id_to_update)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'},
            json=update_data
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 422)
        self.assertEqual(actual.get("error"),
                         "The key \"John Pork\" is not allowed.")

    # Tests for deletion
    def test_delete_platform(self):
        # given
        platform_data = {
            "name": "Test Platform",
            "base_url": "www.test-platform.com/",
            "icon_url": "www.test-platform.com/icon",
            "enabled": True
        }
        admin_user = self.fixtures.admin_user

        created_platform, cleanup = self.factory.platforms.create(
            PlatformCreate(**platform_data))
        self.addCleanup(cleanup)

        id_to_delete = created_platform._id

        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)
        # when
        response_delete = self.app.delete(
            f'/v1/admin/platforms/{str(id_to_delete)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        response_get = self.app.get(
            f'/v1/admin/platforms/{str(id_to_delete)}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        deleted_info = response_delete.get_json().get("data").get("deleted_platform")
        retrieved_info = response_get.get_json().get("data")

        # then
        self.assertEqual(response_delete.status_code, 200)
        self.assertEqual(deleted_info.get("name"), created_platform.name)
        self.assertIsNone(retrieved_info)

    def test_fails_to_delete_a_nonexistent_platform(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        nonexistent_id = ObjectId()

        # when
        response = self.app.delete(
            f'/v1/admin/platforms/{nonexistent_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(actual.get("error"), "\"Platform\" not found.")

    def test_fails_to_delete_a_platform_by_an_invalid_id(self):
        admin_user = self.fixtures.admin_user
        tokens = self.factory.logins.login(
            admin_user.email, constants.strong_password)

        invalid_id = "123"

        # when
        response = self.app.delete(
            f'/v1/admin/platforms/{invalid_id}',
            headers={"Authorization": f'Bearer {tokens.id_token}'}
        )
        actual = response.get_json()

        # then
        self.assertEqual(response.status_code, 500)
        self.assertEqual(actual.get("error"),
                         "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")
