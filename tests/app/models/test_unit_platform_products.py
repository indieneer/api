from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument

from app.models.exceptions import NotFoundException
from app.models.platform_products import PlatformProductsModel, PlatformProductCreate, PlatformProduct, PlatformProductPatch
from tests import UnitTest
from tests.mocks.database import mock_collection
from app.models.price import Price

# Fixture with the Price import
platform_product_fixture = PlatformProduct(
    platform_id=1,
    prices=[Price(currency="USD", value=8.0)],
    product_page_url="https://www.example.com"
)


class PlatformProductTestCase(UnitTest):

    @patch("app.models.platform_products.Database")
    def test_create_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'platform_products')

        def creates_and_returns_a_platform_product():
            # given
            model = PlatformProductsModel(db)
            mock_platform_product = platform_product_fixture.clone()
            collection_mock.insert_one.return_value = mock_platform_product.to_json()

            expected_input = PlatformProductCreate(
                platform_id=mock_platform_product.platform_id,
                prices=mock_platform_product.prices,
                product_page_url=mock_platform_product.product_page_url
            )

            expected_result = mock_platform_product

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.platform_id, expected_result.platform_id)
            self.assertEqual(result.product_page_url, expected_result.product_page_url)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.platform_products.Database")
    def test_get_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'platform_products')

        def gets_and_returns_platform_product():
            # given
            model = PlatformProductsModel(db)
            platform_product_id = ObjectId()
            mock_platform_product = platform_product_fixture.clone()
            collection_mock.find_one.return_value = mock_platform_product.to_json()

            # when
            result = model.get(str(platform_product_id))

            # then
            self.assertEqual(result.platform_id, mock_platform_product.platform_id)
            collection_mock.find_one.assert_called_once_with({'_id': platform_product_id})

        def fails_to_get_platform_product_because_id_is_invalid():
            # given
            model = PlatformProductsModel(db)
            invalid_platform_product_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_platform_product_id)

        def fails_to_get_a_nonexistent_platform_product():
            # given
            model = PlatformProductsModel(db)
            nonexistent_platform_product_id = ObjectId()
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_platform_product_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_platform_product_id})

        tests = [
            gets_and_returns_platform_product,
            fails_to_get_platform_product_because_id_is_invalid,
            fails_to_get_a_nonexistent_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.platform_products.Database")
    def test_patch_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'platform_products')

        def patches_and_returns_updated_platform_product():
            # given
            model = PlatformProductsModel(db)
            platform_product_id = ObjectId()
            updated_platform_product = platform_product_fixture.clone()
            updated_platform_product.prices = [Price(currency="EUR", value=10.0)]
            updated_platform_product.product_page_url = "https://www.updated-example.com"
            collection_mock.find_one_and_update.return_value = updated_platform_product.to_json()

            update_data = PlatformProductPatch(
                platform_id=updated_platform_product.platform_id,
                prices=updated_platform_product.prices,
                product_page_url=updated_platform_product.product_page_url
            )

            # when
            result = model.patch(str(platform_product_id), update_data)

            # then
            self.assertEqual(result.product_page_url, update_data.product_page_url)
            collection_mock.find_one_and_update.assert_called_once_with(
                {'_id': platform_product_id},
                {'$set': update_data.to_json()},
                return_document=ReturnDocument.AFTER
            )

        def fails_to_patch_a_platform_product_because_id_is_invalid():
            # given
            model = PlatformProductsModel(db)
            invalid_platform_product_id = "invalid_id"
            update_data = platform_product_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_platform_product_id, update_data)

        def fails_to_patch_a_nonexistent_platform_product():
            # given
            model = PlatformProductsModel(db)
            nonexistent_platform_product_id = ObjectId()
            update_data = platform_product_fixture.clone()
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_platform_product_id), update_data)

        tests = [
            patches_and_returns_updated_platform_product,
            fails_to_patch_a_platform_product_because_id_is_invalid,
            fails_to_patch_a_nonexistent_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)

    @patch("app.models.platform_products.Database")
    def test_delete_platform_product(self, db: MagicMock):
        collection_mock = mock_collection(db, 'platform_products')

        def deletes_and_confirms_deletion():
            # given
            model = PlatformProductsModel(db)
            platform_product_id = ObjectId()
            mock_platform_product = platform_product_fixture.clone()
            collection_mock.find_one_and_delete.return_value = mock_platform_product.to_json()

            # when
            result = model.delete(str(platform_product_id))

            # then
            self.assertEqual(result.platform_id, mock_platform_product.platform_id)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': platform_product_id})

        def fails_to_delete_a_platform_product_because_id_is_invalid():
            # given
            model = PlatformProductsModel(db)
            invalid_platform_product_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_platform_product_id)

        def fails_to_delete_a_nonexistent_platform_product():
            # given
            model = PlatformProductsModel(db)
            nonexistent_platform_product_id = ObjectId()
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_platform_product_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_platform_product_because_id_is_invalid,
            fails_to_delete_a_nonexistent_platform_product
        ]

        self.run_subtests(tests, after_each=collection_mock.reset_mock)
