from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify
import datetime

from app.models.exceptions import NotFoundException
from app.models.affiliates import AffiliatesModel, AffiliateCreate, Affiliate, AffiliatePatch
from tests import UnitTest
from tests.mocks.database import mock_collection

# TODO: Create a separate fixtures entity for unit tests
affiliate_fixture = Affiliate(
    name="John Doe Affiliate",
    slug="john-doe-affiliate",
    became_seller_at=datetime.datetime(2020, 1, 1),
    enabled=True,
    sales=100,
    code="DOE100",
    bio="A top selling affiliate.",
    logo_url="https://example.com/john_doe_logo.png"
)


class AffiliateTestCase(UnitTest):

    @patch("app.models.affiliates.Database")
    def test_create_affiliate(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliates')

        def creates_and_returns_an_affiliate():
            # given
            model = AffiliatesModel(db)
            mock_affiliate = affiliate_fixture.clone()
            collection_mock.insert_one.return_value = mock_affiliate.to_json()

            expected_input = AffiliateCreate(
                name=mock_affiliate.name,
                slug=mock_affiliate.slug,
                became_seller_at=mock_affiliate.became_seller_at,
                enabled=mock_affiliate.enabled,
                sales=mock_affiliate.sales,
                code=mock_affiliate.code,
                bio=mock_affiliate.bio,
                logo_url=mock_affiliate.logo_url
            )

            expected_result = mock_affiliate

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.name, expected_result.name)
            self.assertEqual(result.slug, slugify(expected_result.name))
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_an_affiliate
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.affiliates.Database")
    def test_get_affiliate(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliates')

        def gets_and_returns_affiliate():
            # given
            model = AffiliatesModel(db)
            affiliate_id = ObjectId()
            mock_affiliate = affiliate_fixture.clone()
            collection_mock.find_one.return_value = mock_affiliate.to_json()

            # when
            result = model.get(str(affiliate_id))

            # then
            self.assertEqual(result.name, mock_affiliate.name)
            collection_mock.find_one.assert_called_once_with({'_id': affiliate_id})

        def fails_to_get_affiliate_because_id_is_invalid():
            # given
            model = AffiliatesModel(db)
            invalid_affiliate_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_affiliate_id)

        def fails_to_get_a_nonexistent_affiliate():
            # given
            model = AffiliatesModel(db)
            nonexistent_affiliate_id = ObjectId()
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_affiliate_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_affiliate_id})

        tests = [
            gets_and_returns_affiliate,
            fails_to_get_affiliate_because_id_is_invalid,
            fails_to_get_a_nonexistent_affiliate
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.affiliates.Database")
    def test_patch_affiliate(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliates')

        def patches_and_returns_updated_affiliate():
            # given
            model = AffiliatesModel(db)
            affiliate_id = ObjectId()
            updated_affiliate = affiliate_fixture.clone()
            updated_affiliate.name = "New name"
            collection_mock.find_one_and_update.return_value = updated_affiliate.to_json()

            update_data = AffiliatePatch(
                name="New name",
                slug=updated_affiliate.slug,
                became_seller_at=updated_affiliate.became_seller_at.isoformat(),
                enabled=updated_affiliate.enabled,
                sales=updated_affiliate.sales,
                code=updated_affiliate.code,
                bio=updated_affiliate.bio,
                logo_url=updated_affiliate.logo_url
            )

            # when
            result = model.patch(str(affiliate_id), update_data)

            # then
            self.assertEqual(result.name, updated_affiliate.name)
            collection_mock.find_one_and_update.assert_called_once_with(
                {'_id': affiliate_id},
                {'$set': update_data.to_bson()},
                return_document=ReturnDocument.AFTER
            )

        def fails_to_patch_an_affiliate_because_id_is_invalid():
            # given
            model = AffiliatesModel(db)
            invalid_affiliate_id = "invalid_id"
            update_data = affiliate_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_affiliate_id, update_data)

        def fails_to_patch_a_nonexistent_affiliate():
            # given
            model = AffiliatesModel(db)
            nonexistent_affiliate_id = ObjectId()
            update_data = affiliate_fixture.clone()
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_affiliate_id), update_data)

        tests = [
            patches_and_returns_updated_affiliate,
            fails_to_patch_an_affiliate_because_id_is_invalid,
            fails_to_patch_a_nonexistent_affiliate
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.affiliates.Database")
    def test_delete_affiliate(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliates')

        def deletes_and_confirms_deletion():
            # given
            model = AffiliatesModel(db)
            affiliate_id = ObjectId()
            mock_affiliate = affiliate_fixture.clone()
            collection_mock.find_one_and_delete.return_value = mock_affiliate.to_json()

            # when
            result = model.delete(str(affiliate_id))

            # then
            self.assertEqual(result.name, mock_affiliate.name)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': affiliate_id})

        def fails_to_delete_an_affiliate_because_id_is_invalid():
            # given
            model = AffiliatesModel(db)
            invalid_affiliate_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_affiliate_id)

        def fails_to_delete_a_nonexistent_affiliate():
            # given
            model = AffiliatesModel(db)
            nonexistent_affiliate_id = ObjectId()
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_affiliate_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_an_affiliate_because_id_is_invalid,
            fails_to_delete_a_nonexistent_affiliate
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)
