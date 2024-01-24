from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify

from app.models.exceptions import NotFoundException
from app.models.platforms import PlatformsModel, PlatformCreate, Platform, PlatformPatch
from tests import UnitTest

# TODO: Create a separate fixtures entity for unit tests
platform_fixture = Platform(
    name="Test platform",
    base_url="www.test-platform.com",
    enabled=True,
    icon_url="www.test-platform.com/icon.svg"
)


class PlatformTestCase(UnitTest):

    @patch("app.models.platforms.Database")
    def test_create_platform(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_a_platform():
            # given
            model = PlatformsModel(db)
            mock_platform = platform_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = PlatformCreate(
                name=mock_platform.name,
                base_url=mock_platform.base_url,
                enabled=mock_platform.enabled,
                icon_url=mock_platform.icon_url
            )

            expected_result = mock_platform

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.name, expected_result.name)
            self.assertEqual(result.slug, slugify(expected_result.name))
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_platform
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.platforms.Database")
    def test_get_platform(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_platform():
            # given
            model = PlatformsModel(db)
            platform_id = ObjectId()
            mock_platform = platform_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_platform.to_json()

            # when
            result = model.get(str(platform_id))

            # then
            self.assertEqual(result.name, mock_platform.name)
            collection_mock.find_one.assert_called_once_with({'_id': platform_id})

        def fails_to_get_platform_because_id_is_invalid():
            # given
            model = PlatformsModel(db)
            invalid_platform_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_platform_id)

        def fails_to_get_a_nonexistent_platform():
            # given
            model = PlatformsModel(db)
            nonexistent_platform_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_platform_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_platform_id})

        tests = [
            gets_and_returns_platform,
            fails_to_get_platform_because_id_is_invalid,
            fails_to_get_a_nonexistent_platform
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.platforms.Database")
    def test_patch_platform(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_platform():
            # given
            model = PlatformsModel(db)
            platform_id = ObjectId()
            updated_platform = platform_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_platform.to_json()

            update_data = PlatformPatch(
                name="New name",
                base_url=updated_platform.base_url,
                enabled=updated_platform.enabled,
                icon_url=updated_platform.icon_url,
                slug="new-name"
            )

            # when
            result = model.patch(str(platform_id), update_data)

            # then
            self.assertEqual(result.name, updated_platform.name)
            collection_mock.find_one_and_update.assert_called_once_with(
                {'_id': platform_id},
                {'$set': update_data.to_bson()},
                return_document=ReturnDocument.AFTER
            )

        def fails_to_patch_a_platform_because_id_is_invalid():
            # given
            model = PlatformsModel(db)
            invalid_platform_id = "invalid_id"
            update_data = platform_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_platform_id, update_data)

        def fails_to_patch_a_nonexistent_platform():
            # given
            model = PlatformsModel(db)
            nonexistent_platform_id = ObjectId()
            update_data = platform_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_platform_id), update_data)

        tests = [
            patches_and_returns_updated_platform,
            fails_to_patch_a_platform_because_id_is_invalid,
            fails_to_patch_a_nonexistent_platform
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.platforms.Database")
    def test_delete_platform(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = PlatformsModel(db)
            platform_id = ObjectId()
            mock_platform = platform_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_platform.to_json()

            # when
            result = model.delete(str(platform_id))

            # then
            self.assertEqual(result.name, mock_platform.name)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': platform_id})

        def fails_to_delete_a_platform_because_id_is_invalid():
            # given
            model = PlatformsModel(db)
            invalid_platform_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_platform_id)

        def fails_to_delete_a_nonexistent_platform():
            # given
            model = PlatformsModel(db)
            nonexistent_platform_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_platform_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_platform_because_id_is_invalid,
            fails_to_delete_a_nonexistent_platform
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()
