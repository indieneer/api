from unittest.mock import patch, MagicMock

from bson import ObjectId

from app.models import SearchedProductModel
from tests import UnitTest


class SearchedProductTestCase(UnitTest):
    @patch("app.models.searched_product.Database")
    def test_search_products(self, db: MagicMock):
        db_connection_mock = db.connection

        def searches_products():
            # given
            model = SearchedProductModel(db)
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            mock_search_product = {
                "_id": ObjectId(),
                "name": "Test product",
                "slug": "test-product",
                "short_description": "A test product",
                "genres": ["Test genre"],
                "publishers": ["Test publisher"],
                "price": {},
                "is_free": False,
                "developers": ["Test developer"],
                "media": {"header_url": "https://example.com"},
                "platforms_os": ["Windows"]
            }
            product_object_ids = [mock_search_product["_id"]]
            collection_mock.aggregate.return_value = [mock_search_product]

            # when
            result = model.search_products(product_object_ids)

            # then
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, mock_search_product["name"])
            collection_mock.aggregate.assert_called_once()

        def searches_products_with_empty_list():
            # given
            model = SearchedProductModel(db)
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            product_object_ids = []
            collection_mock.aggregate.return_value = []

            # when
            result = model.search_products(product_object_ids)

            # then
            self.assertEqual(len(result), 0)
            collection_mock.aggregate.assert_called_once()

        def searches_products_with_not_existing_id():
            # given
            model = SearchedProductModel(db)
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            product_object_ids = [ObjectId()]
            collection_mock.aggregate.return_value = []

            # when
            result = model.search_products(product_object_ids)

            # then
            self.assertEqual(len(result), 0)
            collection_mock.aggregate.assert_called_once()

        tests = [
            searches_products,
            searches_products_with_empty_list,
            searches_products_with_not_existing_id
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_connection_mock.reset_mock()
