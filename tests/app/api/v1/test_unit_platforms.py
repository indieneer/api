from unittest.mock import patch, MagicMock
from app.api.v1.platforms import get_platforms
from app.models.platforms import Platform

from tests import UnitTest


class PlatformsTestCase(UnitTest):

    @patch("app.api.v1.platforms.get_models")
    def test_get_all_platforms(self, get_models: MagicMock):
        endpoint = "/platforms"
        self.app.route(endpoint)(get_platforms)

        get_all_platforms_mock = get_models.return_value.platforms.get_all

        def call_api():
            return self.test_client.get(
                endpoint,
                content_type='application/json'
            )

        def returns_list_of_platforms():
            # given
            mock_platforms = [
                Platform(name="Test platform 1", base_url="www.test-platform1.com", enabled=True, icon_url="www.test-platform1.com/icon.svg").to_json(),
                Platform(name="Test platform 2", base_url="www.test-platform2.com", enabled=False, icon_url="www.test-platform2.com/icon.svg").to_json(),
                Platform(name="Test platform 3", base_url="www.test-platform3.com", enabled=True, icon_url="www.test-platform3.com/icon.svg").to_json()
            ]
            get_all_platforms_mock.return_value = mock_platforms

            expected_response = {
                "status": "ok",
                "data": mock_platforms
            }

            # when
            response = call_api()

            # then
            self.assertNotEqual(len(response.get_json()['data']), 0)
            for platform_data in response.get_json()['data']:
                self.assertIn('name', platform_data)
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)

        tests = [returns_list_of_platforms]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_all_platforms_mock.reset_mock()
