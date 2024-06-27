from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify
import datetime

from app.models.affiliates import Affiliate
from app.models.exceptions import NotFoundException
from app.models.affiliate_platform_products import AffiliatePlatformProductsModel, AffiliatePlatformProductCreate, AffiliatePlatformProduct, AffiliatePlatformProductPatch
from app.models.products import Product, Price, Media, Movie, Resolution, Screenshot, Requirements, \
    PlatformOsRequirements, ReleaseDate
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

affiliate_platform_product_fixture = AffiliatePlatformProduct(
    affiliate_id=str(affiliate_fixture._id),
    affiliate=affiliate_fixture.to_dict(),
    buy_page_url="https://www.example.com",
    prices=[],
    promotions=[],
    platform_product_id="65f9d1648194a472c9f835ce",
    product_id=str(product_fixture._id)
)

affiliate_platform_product_fixture.affiliate = affiliate_fixture
affiliate_platform_product_fixture.product = product_fixture


class AffiliatePlatformProductTestCase(UnitTest):

    @patch("app.models.affiliate_platform_products.Database")
    def test_create_affiliate_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliate_platform_products')

        def creates_and_returns_an_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            collection_mock.insert_one.return_value = mock_affiliate_platform_product.to_json()

            expected_input = AffiliatePlatformProductCreate(
                affiliate_id=mock_affiliate_platform_product.affiliate_id,
                buy_page_url=mock_affiliate_platform_product.buy_page_url,
                prices=mock_affiliate_platform_product.prices,
                promotions=mock_affiliate_platform_product.promotions,
                platform_product_id=mock_affiliate_platform_product.platform_product_id,
                product_id=mock_affiliate_platform_product.product_id
            )

            expected_result = mock_affiliate_platform_product

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.buy_page_url, expected_result.buy_page_url)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_an_affiliate_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.affiliate_platform_products.Database")
    def test_get_affiliate_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliate_platform_products')

        def gets_and_returns_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            affiliate_platform_product_id = ObjectId()
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            collection_mock.aggregate.return_value = [mock_affiliate_platform_product.to_json()]

            # when
            result = model.get(str(affiliate_platform_product_id))

            # then
            self.assertEqual(result.buy_page_url, mock_affiliate_platform_product.buy_page_url)
            collection_mock.aggregate.assert_called_once()

        def fails_to_get_affiliate_platform_product_because_id_is_invalid():
            # given
            model = AffiliatePlatformProductsModel(db)
            invalid_affiliate_platform_product_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_affiliate_platform_product_id)

        def fails_to_get_a_nonexistent_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            nonexistent_affiliate_platform_product_id = ObjectId()
            collection_mock.aggregate.return_value = None

            # when
            result = model.get(str(nonexistent_affiliate_platform_product_id))

            # then
            self.assertIsNone(result)
            collection_mock.aggregate.assert_called_once()

        tests = [
            gets_and_returns_affiliate_platform_product,
            fails_to_get_affiliate_platform_product_because_id_is_invalid,
            fails_to_get_a_nonexistent_affiliate_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.affiliate_platform_products.Database")
    def test_patch_affiliate_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliate_platform_products')

        def patches_and_returns_updated_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            affiliate_platform_product_id = ObjectId()
            updated_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            updated_affiliate_platform_product.buy_page_url = "https://www.example.com/new"
            collection_mock.find_one_and_update.return_value = updated_affiliate_platform_product.to_json()

            update_data = AffiliatePlatformProductPatch(
                buy_page_url=updated_affiliate_platform_product.buy_page_url
            )

            # when
            result = model.patch(str(affiliate_platform_product_id), update_data)

            # then
            self.assertEqual(result.buy_page_url, updated_affiliate_platform_product.buy_page_url)

        def fails_to_patch_an_affiliate_platform_product_because_id_is_invalid():
            # given
            model = AffiliatePlatformProductsModel(db)
            invalid_affiliate_platform_product_id = "invalid_id"
            update_data = affiliate_platform_product_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_affiliate_platform_product_id, update_data)

        def fails_to_patch_a_nonexistent_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            nonexistent_affiliate_platform_product_id = ObjectId()
            update_data = affiliate_platform_product_fixture.clone()
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_affiliate_platform_product_id), update_data)

        tests = [
            patches_and_returns_updated_affiliate_platform_product,
            fails_to_patch_an_affiliate_platform_product_because_id_is_invalid,
            fails_to_patch_a_nonexistent_affiliate_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.affiliate_platform_products.Database")
    def test_delete_affiliate_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'affiliate_platform_products')

        def deletes_and_confirms_deletion():
            # given
            model = AffiliatePlatformProductsModel(db)
            affiliate_platform_product_id = ObjectId()
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            collection_mock.find_one_and_delete.return_value = mock_affiliate_platform_product.to_json()

            # when
            result = model.delete(str(affiliate_platform_product_id))

            # then
            self.assertEqual(result.buy_page_url, mock_affiliate_platform_product.buy_page_url)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': affiliate_platform_product_id})

        def fails_to_delete_an_affiliate_platform_product_because_id_is_invalid():
            # given
            model = AffiliatePlatformProductsModel(db)
            invalid_affiliate_platform_product_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_affiliate_platform_product_id)

        def fails_to_delete_a_nonexistent_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            nonexistent_affiliate_platform_product_id = ObjectId()
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_affiliate_platform_product_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_an_affiliate_platform_product_because_id_is_invalid,
            fails_to_delete_a_nonexistent_affiliate_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)
