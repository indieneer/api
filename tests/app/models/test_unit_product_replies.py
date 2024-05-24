from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify
import datetime

from app.models.product_comments import ProductComment
from app.models.profiles import Profile
from app.models.exceptions import NotFoundException
from app.models.product_replies import ProductRepliesModel, ProductReplyCreate, ProductReply, ProductReplyPatch
from app.models.products import Product, Price, Media, Movie, Resolution, Screenshot, Requirements, \
    PlatformOsRequirements, ReleaseDate
from tests import UnitTest

# TODO: Create a separate fixtures entity for unit tests
profile_fixture = Profile(
    display_name="Pork",
    email="john_pork@gmail.com",
    idp_id="test",
    nickname="PORKEY",
    photo_url="https://www.example.com/pork_pfp",
    roles=[]
)

product_comment_fixture = ProductComment(
    product_id=ObjectId(),
    profile_id=ObjectId(),
    text="Ok"
)

product_reply_fixture = ProductReply(
    comment_id=str(product_comment_fixture._id),
    profile_id=str(profile_fixture._id),
    text="Test text"
)


class ProductReplyTestCase(UnitTest):

    @patch("app.models.product_replies.Database")
    def test_create_product_reply(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_a_product_reply():
            # given
            model = ProductRepliesModel(db)
            mock_product_reply = product_reply_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = ProductReplyCreate(
                comment_id=mock_product_reply.comment_id,
                profile_id=mock_product_reply.profile_id,
                text=mock_product_reply.text
            )

            expected_result = mock_product_reply

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.text, expected_result.text)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_product_reply
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.product_replies.Database")
    def test_get_product_reply(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_product_reply():
            # given
            model = ProductRepliesModel(db)
            product_reply_id = ObjectId()
            mock_product_reply = product_reply_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_product_reply.to_json()

            # when
            result = model.get(str(product_reply_id))

            # then
            self.assertEqual(result.text, mock_product_reply.text)
            collection_mock.find_one.assert_called_once()

        tests = [
            gets_and_returns_product_reply
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.product_replies.Database")
    def test_patch_product_reply(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_product_reply():
            # given
            model = ProductRepliesModel(db)
            product_reply_id = ObjectId()
            updated_product_reply = product_reply_fixture.clone()
            updated_product_reply.text = "Updated text"
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_product_reply.to_json()

            update_data = ProductReplyPatch(
                text=updated_product_reply.text
            )

            # when
            result = model.patch(str(product_reply_id), update_data)

            # then
            self.assertEqual(result.text, updated_product_reply.text)

        tests = [
            patches_and_returns_updated_product_reply
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.product_replies.Database")
    def test_delete_product_reply(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = ProductRepliesModel(db)
            product_reply_id = ObjectId()
            mock_product_reply = product_reply_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_product_reply.to_json()

            # when
            result = model.delete(str(product_reply_id))

            # then
            self.assertEqual(result.text, mock_product_reply.text)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': product_reply_id})

        def fails_to_delete_a_product_reply_because_id_is_invalid():
            # given
            model = ProductRepliesModel(db)
            invalid_product_reply_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_product_reply_id)

        def fails_to_delete_a_nonexistent_product_reply():
            # given
            model = ProductRepliesModel(db)
            nonexistent_product_reply_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_product_reply_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_product_reply_because_id_is_invalid,
            fails_to_delete_a_nonexistent_product_reply
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()
