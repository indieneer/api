from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument

from app.models.exceptions import NotFoundException
from app.models.operating_systems import OperatingSystemsModel, OperatingSystemCreate, OperatingSystem, OperatingSystemPatch
from tests import UnitTest


class OperatingSystemTestCase(UnitTest):

    @patch("app.models.operating_systems.Database")
    def test_create_operating_system(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_an_operating_system():
            # given
            model = OperatingSystemsModel(db)
            mock_operating_system = OperatingSystem(name="Test OS")
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = OperatingSystemCreate(
                name=mock_operating_system.name
            )

            expected_result = mock_operating_system

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.name, expected_result.name)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_an_operating_system
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.operating_systems.Database")
    def test_get_operating_system(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_operating_system():
            # given
            model = OperatingSystemsModel(db)
            os_id = ObjectId()
            mock_operating_system = OperatingSystem(name="Test OS")
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_operating_system.to_json()

            # when
            result = model.get(str(os_id))

            # then
            self.assertEqual(result.name, mock_operating_system.name)
            collection_mock.find_one.assert_called_once_with({'_id': os_id})

        def fails_to_get_operating_system_because_id_is_invalid():
            # given
            model = OperatingSystemsModel(db)
            invalid_os_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_os_id)

        def fails_to_get_a_nonexistent_operating_system():
            # given
            model = OperatingSystemsModel(db)
            nonexistent_os_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_os_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_os_id})

        tests = [
            gets_and_returns_operating_system,
            fails_to_get_operating_system_because_id_is_invalid,
            fails_to_get_a_nonexistent_operating_system
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.operating_systems.Database")
    def test_patch_operating_system(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_operating_system():
            # given
            model = OperatingSystemsModel(db)
            os_id = ObjectId()
            updated_operating_system = OperatingSystem(name="Updated OS")
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_operating_system.to_json()

            update_data = OperatingSystemPatch(
                name=updated_operating_system.name
            )

            # when
            result = model.patch(str(os_id), update_data)

            # then
            self.assertEqual(result.name, updated_operating_system.name)
            collection_mock.find_one_and_update.assert_called_once_with(
                {'_id': os_id},
                {'$set': update_data.to_bson()},
                return_document=ReturnDocument.AFTER
            )

        def fails_to_patch_an_operating_system_because_id_is_invalid():
            # given
            model = OperatingSystemsModel(db)
            invalid_os_id = "invalid_id"
            update_data = OperatingSystemPatch(name="Updated OS")

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_os_id, update_data)

        def fails_to_patch_a_nonexistent_operating_system():
            # given
            model = OperatingSystemsModel(db)
            nonexistent_os_id = ObjectId()
            update_data = OperatingSystemPatch(name="Updated OS")
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_os_id), update_data)

        tests = [
            patches_and_returns_updated_operating_system,
            fails_to_patch_an_operating_system_because_id_is_invalid,
            fails_to_patch_a_nonexistent_operating_system
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.operating_systems.Database")
    def test_delete_operating_system(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = OperatingSystemsModel(db)
            os_id = ObjectId()
            mock_operating_system = OperatingSystem("Test OS")
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_operating_system.to_json()

            # when
            result = model.delete(str(os_id))

            # then
            self.assertEqual(result.name, mock_operating_system.name)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': os_id})

        def fails_to_delete_an_operating_system_because_id_is_invalid():
            # given
            model = OperatingSystemsModel(db)
            invalid_os_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_os_id)

        def fails_to_delete_a_nonexistent_operating_system():
            # given
            model = OperatingSystemsModel(db)
            nonexistent_os_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_os_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_an_operating_system_because_id_is_invalid,
            fails_to_delete_a_nonexistent_operating_system
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()