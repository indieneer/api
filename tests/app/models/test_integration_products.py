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
        self.assertIsNotNone(retrieved_product)
        self.assertEqual(product.name, retrieved_product.name)

    def test_create_product(self):
        # given
        product = self.fixtures.product.clone()

        # when
        created_product = self.models.products.create(product)
        self.addCleanup(lambda: self.factory.products.cleanup(product._id))

        # then
        self.assertIsNotNone(created_product)
        self.assertEqual(created_product.name, product.name)
        self.assertEqual(created_product.detailed_description, product.detailed_description)

    def test_patch_product(self):
        products_model = ProductsModel(self.services.db)

        # given
        product = self.fixtures.product.clone()
        patch_data = ProductPatch(name="Updated Name")

        created_product, cleanup = self.factory.products.create(product)
        self.addCleanup(cleanup)

        # when
        updated_product = products_model.patch(str(created_product._id), patch_data)

        # then
        self.assertIsNotNone(updated_product)
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
