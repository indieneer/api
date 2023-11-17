from app.main import app
from app.models.products import ProductsModel, ProductPatch, ProductCreate, Product
from tests.integration_test import IntegrationTest
from copy import deepcopy


class ProductsModelTestCase(IntegrationTest):

    def test_get_product(self):
        products_model = ProductsModel(self.services.db)

        # given
        product = self.fixtures.product

        # when
        retrieved_product = products_model.get(str(product._id))

        # then
        if retrieved_product is None:
            self.assertIsNotNone(retrieved_product)
        else:
            self.assertEqual(product._id, retrieved_product._id)

    def test_patch_product(self):
        products_model = ProductsModel(self.services.db)

        # given
        product = self.fixtures.product
        patch_data = ProductPatch(name="Updated Name")

        # when
        updated_product = products_model.patch(str(product._id), patch_data)

        # then
        if updated_product is None:
            self.assertIsNotNone(updated_product)
        else:
            self.assertEqual(updated_product.name, "Updated Name")

    def test_delete_product(self):
        products_model = ProductsModel(self.services.db)
        # given
        product, cleanup = self.factory.products.create(
            self.fixtures.product.clone())
        self.addCleanup(cleanup)

        # when
        deleted_count = products_model.delete(str(product._id))
        retrieved_product_after_deletion = products_model.get(str(product._id))

        # then
        self.assertEqual(deleted_count, 1)
        self.assertIsNone(retrieved_product_after_deletion)
