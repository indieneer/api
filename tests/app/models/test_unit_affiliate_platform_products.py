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

# TODO: Create a separate fixtures entity for unit tests
affiliate_platform_product_fixture = AffiliatePlatformProduct(
    affiliate_id=ObjectId("65f9d1648194a472c9f835cd"),
    buy_page_url="https://www.example.com",
    prices=[],
    promotions=[],
    affiliate=Affiliate(
        name="John Doe Affiliate",
        slug="john-doe-affiliate",
        became_seller_at=datetime.datetime(2020, 1, 1),
        enabled=True,
        sales=100,
        code="DOE100",
        bio="A top selling affiliate.",
        logo_url="https://example.com/john_doe_logo.png"
    ).clone(),
    platform_product_id=ObjectId("65f9d1648194a472c9f835ce"),
    product=Product(
        name="Geometry Dash",
        type="Game",
        slug="geometry-dash",
        required_age=0,
        short_description="GD",
        detailed_description="Geometry dash cool game real",
        is_free=False,
        platforms={"steam": "https://store.steampowered.com/app/322170/Geometry_Dash/"},
        price={
            "USD": Price(currency="USD", initial=199, final=199, final_formatted="$1.99")
        },
        supported_languages=["English"],
        media=Media(
            background_url="https://example.com",
            header_url="https://example.com",
            movies=[
                Movie(
                    name="Trailer",
                    thumbnail_url="https://example.com",
                    formats={
                        "webm": Resolution(px480="https://example.com/480.webm",
                                           max="https://example.com/max.webm"),
                        "mp4": Resolution(px480="https://example.com/480.mp4",
                                          max="https://example.com/max.mp4"),
                    }
                )
            ],
            screenshots=[
                Screenshot(thumbnail_url="https://example.com/thumbnail1.jpg",
                           full_url="https://example.com/full1.jpg"),
                Screenshot(thumbnail_url="https://example.com/thumbnail2.jpg",
                           full_url="https://example.com/full2.jpg"),
            ]
        ),
        requirements=Requirements(
            windows=PlatformOsRequirements(minimum={"minimum": "Avg PC"}, recommended=None),
            mac=PlatformOsRequirements(minimum={"minimum": "Avg Mac"}, recommended=None),
            linux=None
        ),
        developers=["RobTop Games"],
        publishers=["RobTop Games"],
        platforms_os=["windows", "mac"],
        categories=[ObjectId("5f760d432f6812a3d2aabcde")],
        genres=[ObjectId("65022c86878d0eb09c1b7dae")],
        release_date={"date": "2014-12-22", "coming_soon": False}
    ),
    product_id=ObjectId("65f9d1648194a472c9f835cd")
)


class AffiliatePlatformProductTestCase(UnitTest):

    @patch("app.models.affiliate_platform_products.Database")
    def test_create_affiliate_platform_product(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_an_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = AffiliatePlatformProductCreate(
                affiliate_id=mock_affiliate_platform_product.affiliate_id,
                buy_page_url=mock_affiliate_platform_product.buy_page_url,
                prices=mock_affiliate_platform_product.prices,
                promotions=mock_affiliate_platform_product.promotions,
                affiliate=mock_affiliate_platform_product.affiliate,
                platform_product_id=mock_affiliate_platform_product.platform_product_id,
                product=mock_affiliate_platform_product.product,
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

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.affiliate_platform_products.Database")
    def test_get_affiliate_platform_product(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            affiliate_platform_product_id = ObjectId()
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_affiliate_platform_product.to_json()

            # when
            result = model.get(str(affiliate_platform_product_id))

            # then
            self.assertEqual(result.buy_page_url, mock_affiliate_platform_product.buy_page_url)
            collection_mock.find_one.assert_called_once_with({'_id': affiliate_platform_product_id})

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
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_affiliate_platform_product_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_affiliate_platform_product_id})

        tests = [
            gets_and_returns_affiliate_platform_product,
            fails_to_get_affiliate_platform_product_because_id_is_invalid,
            fails_to_get_a_nonexistent_affiliate_platform_product
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.affiliate_platform_products.Database")
    def test_patch_affiliate_platform_product(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_affiliate_platform_product():
            # given
            model = AffiliatePlatformProductsModel(db)
            affiliate_platform_product_id = ObjectId()
            updated_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            updated_affiliate_platform_product.buy_page_url = "https://www.example.com/new"
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

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
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_affiliate_platform_product_id), update_data)

        tests = [
            patches_and_returns_updated_affiliate_platform_product,
            fails_to_patch_an_affiliate_platform_product_because_id_is_invalid,
            fails_to_patch_a_nonexistent_affiliate_platform_product
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()

    @patch("app.models.affiliate_platform_products.Database")
    def test_delete_affiliate_platform_product(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = AffiliatePlatformProductsModel(db)
            affiliate_platform_product_id = ObjectId()
            mock_affiliate_platform_product = affiliate_platform_product_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
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
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_affiliate_platform_product_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_an_affiliate_platform_product_because_id_is_invalid,
            fails_to_delete_a_nonexistent_affiliate_platform_product
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()
