from app.main import app
from app.models.products import ProductsModel, ProductPatch
from tests.integration_test import IntegrationTest


class ProductsModelTestCase(IntegrationTest):

    def test_get_product(self):
        products_model = ProductsModel(self.services.db)

        # given
        product = self.fixtures.product

        # when
        retrieved_product = products_model.get(str(product._id))

        # then
        self.assertEqual(product._id, retrieved_product._id)

    def test_patch_product(self):
        products_model = ProductsModel(self.services.db)

        # given
        product = self.fixtures.product
        patch_data = ProductPatch(name="Updated Name")

        # when
        updated_product = products_model.patch(str(product._id), patch_data)

        # then
        self.assertEqual(updated_product.name, "Updated Name")

    def test_delete_product(self):
        products_model = ProductsModel(self.services.db)

        # given
        product = self.fixtures.product

        # when
        deleted_count = products_model.delete(str(product._id))
        retrieved_product_after_deletion = products_model.get(str(product._id))

        # then
        self.assertEqual(deleted_count, 1)
        self.assertIsNone(retrieved_product_after_deletion)
