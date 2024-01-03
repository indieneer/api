from unittest.mock import patch, MagicMock
import json

from tests import UnitTest
from app.models.platforms import PlatformCreate, Platform, PlatformPatch
from app.middlewares.requires_auth import create_test_token


class PlatformsTestCase(UnitTest):

    @patch("app.api.v1.admin.platforms.get_models")
    def test_create_platform(self, get_models: MagicMock):
        create_platform_mock = get_models.return_value.platforms.create

        def call_api(body):
            return self.app.post(
                "/v1/admin/platforms",
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_platform():
            # given
            mock_platform = Platform(name="Epic Games", base_url="https://store.epicgames.com/", enabled=True, icon_url="icon/url", slug="epic-games")
            create_platform_mock.return_value = mock_platform

            expected_input = PlatformCreate(
                name=mock_platform.name,
                base_url=mock_platform.base_url,
                enabled=mock_platform.enabled,
                icon_url=mock_platform.icon_url
            )

            expected_response = {
                "status": "ok",
                "data": mock_platform.to_json()
            }

            # when
            response = call_api({
                "name": expected_input.name,
                "base_url": expected_input.base_url,
                "enabled": expected_input.enabled,
                "icon_url": expected_input.icon_url
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_platform_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_platform_and_returns_an_error():
            # given
            mock_platform = Platform(name="Epic Games", base_url="https://store.epicgames.com/", enabled=True, icon_url="icon/url", slug="epic-games")
            create_platform_mock.side_effect = Exception("BANG!")

            expected_input = PlatformCreate(
                name=mock_platform.name,
                base_url=mock_platform.base_url,
                enabled=mock_platform.enabled,
                icon_url=mock_platform.icon_url
            )
            expected_response = {
                "status": "error",
                "error": "BANG!"
            }

            # when
            response = call_api({
                "name": expected_input.name,
                "base_url": expected_input.base_url,
                "enabled": expected_input.enabled,
                "icon_url": expected_input.icon_url
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 500)
            create_platform_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_platform_when_body_is_invalid():
            # given
            expected_response = {
                "status": "error",
                "error": "Invalid data provided."
            }

            # when
            response = call_api({
                "email": "test@mail.com",
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            create_platform_mock.assert_not_called()

        tests = [
            creates_and_returns_a_platform,
            fails_to_create_a_platform_and_returns_an_error,
            fails_to_create_a_platform_when_body_is_invalid
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                create_platform_mock.reset_mock()

    @patch("app.api.v1.admin.platforms.get_models")
    def test_get_platform(self, get_models: MagicMock):
        get_platform_mock = get_models.return_value.platforms.get

        def call_api(platform_id):
            return self.app.get(
                f"/v1/admin/platforms/{platform_id}",
                content_type='application/json',
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])}
            )

        def finds_and_returns_a_platform():
            # given
            mock_platform = Platform(name="Epic Games", base_url="https://store.epicgames.com/", enabled=True, icon_url="icon/url", slug="epic-games")
            get_platform_mock.return_value = mock_platform

            expected_response = {
                "status": "ok",
                "data": mock_platform.to_json()
            }

            # when
            response = call_api(mock_platform._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_platform_mock.assert_called_once_with(mock_platform._id)

        def does_not_find_a_platform_and_returns_an_error():
            # given
            mock_id = "1"
            get_platform_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'The platform with ID {mock_id} was not found.'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_platform_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_platform,
            does_not_find_a_platform_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                get_platform_mock.reset_mock()

    @patch("app.api.v1.admin.platforms.get_models")
    def test_patch_platform(self, get_models: MagicMock):
        patch_platform_mock = get_models.return_value.platforms.patch

        def call_api(platform_id, body):
            return self.app.patch(
                f"/v1/admin/platforms/{platform_id}",
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def patches_and_returns_the_platform():
            # given
            mock_platform = Platform(name="Epic Games", base_url="https://store.epicgames.com/", enabled=True, icon_url="icon/url", slug="epic-games")
            patch_platform_mock.return_value = mock_platform

            expected_input = PlatformPatch(
                name=mock_platform.name,
                base_url=mock_platform.base_url,
                enabled=mock_platform.enabled,
                icon_url=mock_platform.icon_url
            )
            expected_response = {
                "status": "ok",
                "data": mock_platform.to_json()
            }

            # when
            response = call_api(mock_platform._id, {
                "name": expected_input.name,
                "base_url": expected_input.base_url,
                "enabled": expected_input.enabled,
                "icon_url": expected_input.icon_url
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            patch_platform_mock.assert_called_once_with(
                str(mock_platform._id), expected_input)

        tests = [
            patches_and_returns_the_platform
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                patch_platform_mock.reset_mock()

    @patch("app.api.v1.admin.platforms.get_models")
    def test_delete_platform(self, get_models: MagicMock):
        self.maxDiff = None
        delete_platform_mock = get_models.return_value.platforms.delete

        def call_api(platform_id):
            return self.app.delete(
                f"/v1/admin/platforms/{platform_id}",
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_platform():
            # given
            mock_platform = Platform(name="Epic Games", base_url="https://store.epicgames.com/", enabled=True,
                                     icon_url="icon/url", slug="epic-games")
            delete_platform_mock.return_value = mock_platform

            expected_response = {
                "status": "ok",
                "data": {"deleted_platform": mock_platform.to_json(), "message": f'Platform id {mock_platform._id} successfully deleted'}
            }

            # when
            response = call_api(mock_platform._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            delete_platform_mock.assert_called_once_with(mock_platform._id)

        def fails_to_delete_a_nonexistent_platform():
            # given
            mock_id = "2"
            delete_platform_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"The platform with ID {mock_id} was not found."
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_platform_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_platform,
            fails_to_delete_a_nonexistent_platform
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                delete_platform_mock.reset_mock()
