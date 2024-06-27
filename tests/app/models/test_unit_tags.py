from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument

from app.models.exceptions import NotFoundException
from app.models.tags import TagsModel

from tests import UnitTest
from tests.mocks.database import mock_collection
from app.models.tags import TagCreate, Tag, TagPatch


class TagsTestCase(UnitTest):

    @patch("app.models.tags.Database")
    def test_create_tag(self, db: MagicMock):
        collection_mock = mock_collection(db, 'tags')

        def creates_and_returns_a_tag():
            # given
            model = TagsModel(db)
            mock_tag = Tag(name="Test tag")

            collection_mock.insert_one.return_value = mock_tag.to_json()

            expected_input = TagCreate(
                name=mock_tag.name
            )

            expected_result = mock_tag

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.name, expected_result.name)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_tag
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.tags.Database")
    def test_get_tag(self, db: MagicMock):
        collection_mock = mock_collection(db, 'tags')

        def gets_and_returns_tag():
            # given
            model = TagsModel(db)
            tag_id = ObjectId()
            mock_tag = Tag(name="Test tag")
            collection_mock.find_one.return_value = mock_tag.to_json()

            # when
            result = model.get(str(tag_id))

            # then
            self.assertEqual(result.name, mock_tag.name)
            collection_mock.find_one.assert_called_once_with({'_id': tag_id})

        def fails_to_get_tag_because_id_is_invalid():
            # given
            model = TagsModel(db)
            invalid_tag_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_tag_id)

        def fails_to_get_a_nonexistent_tag():
            # given
            model = TagsModel(db)
            nonexistent_tag_id = ObjectId()
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_tag_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_tag_id})

        tests = [
            gets_and_returns_tag,
            fails_to_get_tag_because_id_is_invalid,
            fails_to_get_a_nonexistent_tag
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.tags.Database")
    def test_patch_tag(self, db: MagicMock):
        collection_mock = mock_collection(db, 'tags')

        def patches_and_returns_updated_tag():
            # given
            model = TagsModel(db)
            tag_id = ObjectId()
            updated_tag = Tag(name="Updated tag")
            collection_mock.find_one_and_update.return_value = updated_tag.to_json()

            update_data = TagPatch(
                name=updated_tag.name
            )

            # when
            result = model.patch(str(tag_id), update_data)

            # then
            self.assertEqual(result.name, updated_tag.name)
            collection_mock.find_one_and_update.assert_called_once_with(
                {'_id': tag_id},
                {'$set': update_data.to_bson()},
                return_document=ReturnDocument.AFTER
            )

        def fails_to_patch_a_tag_because_id_is_invalid():
            # given
            model = TagsModel(db)
            invalid_tag_id = "invalid_id"
            update_data = TagPatch(name="Updated tag")

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_tag_id, update_data)

        def fails_to_patch_a_nonexistent_tag():
            # given
            model = TagsModel(db)
            nonexistent_tag_id = ObjectId()
            update_data = TagPatch(name="Updated tag")
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_tag_id), update_data)

        tests = [
            patches_and_returns_updated_tag,
            fails_to_patch_a_tag_because_id_is_invalid,
            fails_to_patch_a_nonexistent_tag
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.tags.Database")
    def test_delete_tag(self, db: MagicMock):
        collection_mock = mock_collection(db, 'tags')

        def deletes_and_confirms_deletion():
            # given
            model = TagsModel(db)
            tag_id = ObjectId()
            mock_tag = Tag(name="Test tag")
            collection_mock.find_one_and_delete.return_value = mock_tag.to_json()

            # when
            result = model.delete(str(tag_id))

            # then
            self.assertEqual(result.name, mock_tag.name)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': tag_id})

        def fails_to_delete_a_tag_because_id_is_invalid():
            # given
            model = TagsModel(db)
            invalid_tag_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_tag_id)

        def fails_to_delete_a_nonexistent_tag():
            # given
            model = TagsModel(db)
            nonexistent_tag_id = ObjectId()
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_tag_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_tag_because_id_is_invalid,
            fails_to_delete_a_nonexistent_tag
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)
