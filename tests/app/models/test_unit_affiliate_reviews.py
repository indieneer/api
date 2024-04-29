from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify

from app.models.exceptions import NotFoundException
from app.models.affiliate_reviews import AffiliateReviewsModel, AffiliateReviewCreate, AffiliateReview, AffiliateReviewPatch
from tests import UnitTest

# TODO: Create a separate fixtures entity for unit tests
affiliate_review_fixture = AffiliateReview(
    profile_id="507f1f77bcf86cd799439011",
    affiliate_id="507f1f77bcf86cd799439012",
    affiliate_platform_product_id="507f1f77bcf86cd799439013",
    text="Great product",
    rating=5
)


class AffiliateReviewTestCase(UnitTest):

    @patch("app.models.affiliate_reviews.Database")
    def test_create_affiliate_review(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_an_affiliate_review():
            # given
            model = AffiliateReviewsModel(db)
            mock_affiliate_review = affiliate_review_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = AffiliateReviewCreate(
                profile_id=mock_affiliate_review.profile_id,
                affiliate_id=mock_affiliate_review.affiliate_id,
                affiliate_platform_product_id=mock_affiliate_review.affiliate_platform_product_id,
                text=mock_affiliate_review.text,
                rating=mock_affiliate_review.rating
            )

            expected_result = mock_affiliate_review

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.text, expected_result.text)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_an_affiliate_review
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.affiliate_reviews.Database")
    def test_get_affiliate_review(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_affiliate_review():
            # given
            model = AffiliateReviewsModel(db)
            affiliate_review_id = ObjectId()
            mock_affiliate_review = affiliate_review_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_affiliate_review.to_json()

            # when
            result = model.get(str(affiliate_review_id))

            # then
            self.assertEqual(result.text, mock_affiliate_review.text)
            collection_mock.find_one.assert_called_once_with({'_id': affiliate_review_id})

        def fails_to_get_affiliate_review_because_id_is_invalid():
            # given
            model = AffiliateReviewsModel(db)
            invalid_affiliate_review_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_affiliate_review_id)

        def fails_to_get_a_nonexistent_affiliate_review():
            # given
            model = AffiliateReviewsModel(db)
            nonexistent_affiliate_review_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_affiliate_review_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_affiliate_review_id})

        tests = [
            gets_and_returns_affiliate_review,
            fails_to_get_affiliate_review_because_id_is_invalid,
            fails_to_get_a_nonexistent_affiliate_review
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.affiliate_reviews.Database")
    def test_patch_affiliate_review(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_affiliate_review():
            # given
            model = AffiliateReviewsModel(db)
            affiliate_review_id = ObjectId()
            updated_affiliate_review = affiliate_review_fixture.clone()
            updated_affiliate_review.text = "Updated review text"
            updated_affiliate_review.rating = 4
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_affiliate_review.to_json()

            update_data = AffiliateReviewPatch(
                profile_id=updated_affiliate_review.profile_id,
                affiliate_id=updated_affiliate_review.affiliate_id,
                affiliate_platform_product_id=updated_affiliate_review.affiliate_platform_product_id,
                text=updated_affiliate_review.text,
                rating=updated_affiliate_review.rating
            )

            # when
            result = model.patch(str(updated_affiliate_review._id), update_data)

            # then
            self.assertEqual(result.text, update_data.text)
            collection_mock.find_one_and_update.assert_called_once_with(
                {'_id': updated_affiliate_review._id},
                {'$set': update_data.to_bson()},
                return_document=ReturnDocument.AFTER
            )

        def fails_to_patch_an_affiliate_review_because_id_is_invalid():
            # given
            model = AffiliateReviewsModel(db)
            invalid_affiliate_review_id = "invalid_id"
            update_data = affiliate_review_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_affiliate_review_id, update_data)

        def fails_to_patch_a_nonexistent_affiliate_review():
            # given
            model = AffiliateReviewsModel(db)
            nonexistent_affiliate_review_id = ObjectId()
            update_data = affiliate_review_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_affiliate_review_id), update_data)

        tests = [
            patches_and_returns_updated_affiliate_review,
            fails_to_patch_an_affiliate_review_because_id_is_invalid,
            fails_to_patch_a_nonexistent_affiliate_review
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.affiliate_reviews.Database")
    def test_delete_affiliate_review(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = AffiliateReviewsModel(db)
            affiliate_review_id = ObjectId()
            mock_affiliate_review = affiliate_review_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_affiliate_review.to_json()

            # when
            result = model.delete(str(affiliate_review_id))

            # then
            self.assertEqual(result.text, mock_affiliate_review.text)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': affiliate_review_id})

        def fails_to_delete_an_affiliate_review_because_id_is_invalid():
            # given
            model = AffiliateReviewsModel(db)
            invalid_affiliate_review_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_affiliate_review_id)

        def fails_to_delete_a_nonexistent_affiliate_review():
            # given
            model = AffiliateReviewsModel(db)
            nonexistent_affiliate_review_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_affiliate_review_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_an_affiliate_review_because_id_is_invalid,
            fails_to_delete_a_nonexistent_affiliate_review
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()
