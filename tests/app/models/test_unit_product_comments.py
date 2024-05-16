from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify
import datetime

from app.models.profiles import Profile
from app.models.exceptions import NotFoundException
from app.models.product_comments import ProductCommentsModel, ProductCommentCreate, ProductComment, ProductCommentPatch
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

product_fixture = Product(
    categories=[],
    detailed_description="",
    developers=[],
    genres=[],
    is_free=False,
    media=Media(background_url="", header_url="", movies=[], screenshots=[]),
    name="",
    platforms={},
    platforms_os=[],
    price={},
    publishers=[],
    release_date=ReleaseDate(date=None, coming_soon=False).to_json(),
    required_age=0,
    requirements=Requirements(
        None,
        None,
        None,
    ),
    short_description="",
    slug="",
    type="",
    supported_languages=[]
)

product_comment_fixture = ProductComment(
    product_id=str(product_fixture._id),
    profile_id=str(profile_fixture._id),
    text="Test text"
)


class ProductCommentTestCase(UnitTest):

    @patch("app.models.product_comments.Database")
    def test_create_product_comment(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_a_product_comment():
            # given
            model = ProductCommentsModel(db)
            mock_product_comment = product_comment_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = ProductCommentCreate(
                product_id=mock_product_comment.product_id,
                profile_id=mock_product_comment.profile_id,
                text=mock_product_comment.text
            )

            expected_result = mock_product_comment

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.text, expected_result.text)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_product_comment
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.product_comments.Database")
    def test_get_product_comment(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_product_comment():
            # given
            model = ProductCommentsModel(db)
            product_comment_id = ObjectId()
            mock_product_comment = product_comment_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_product_comment.to_json()

            # when
            result = model.get(str(product_comment_id))

            # then
            self.assertEqual(result.text, mock_product_comment.text)
            collection_mock.find_one.assert_called_once()

        tests = [
            gets_and_returns_product_comment
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.product_comments.Database")
    def test_patch_product_comment(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_product_comment():
            # given
            model = ProductCommentsModel(db)
            product_comment_id = ObjectId()
            updated_product_comment = product_comment_fixture.clone()
            updated_product_comment.text = "Updated text"
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_product_comment.to_json()

            update_data = ProductCommentPatch(
                text=updated_product_comment.text
            )

            # when
            result = model.patch(str(product_comment_id), update_data)

            # then
            self.assertEqual(result.text, updated_product_comment.text)

        tests = [
            patches_and_returns_updated_product_comment
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.product_comments.Database")
    def test_delete_product_comment(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = ProductCommentsModel(db)
            product_comment_id = ObjectId()
            mock_product_comment = product_comment_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_product_comment.to_json()

            # when
            result = model.delete(str(product_comment_id))

            # then
            self.assertEqual(result.text, mock_product_comment.text)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': product_comment_id})

        def fails_to_delete_a_product_comment_because_id_is_invalid():
            # given
            model = ProductCommentsModel(db)
            invalid_product_comment_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_product_comment_id)

        def fails_to_delete_a_nonexistent_product_comment():
            # given
            model = ProductCommentsModel(db)
            nonexistent_product_comment_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_product_comment_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_product_comment_because_id_is_invalid,
            fails_to_delete_a_nonexistent_product_comment
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()
