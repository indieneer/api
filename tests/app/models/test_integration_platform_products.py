from app.models.platform_products import PlatformProductsModel, PlatformProductPatch, PlatformProductCreate
from tests.integration_test import IntegrationTest
from dataclasses import fields


class PlatformProductsModelTestCase(IntegrationTest):

    def test_get_platform_product(self):
        platform_products_model = PlatformProductsModel(self.services.db)

        # given
        platform_product_fixture = self.fixtures.platform_product

        # when
        retrieved_platform_product = platform_products_model.get(str(platform_product_fixture._id))

        # then
        self.assertIsNotNone(retrieved_platform_product)
        self.assertEqual(platform_product_fixture.platform_id, retrieved_platform_product.platform_id)

    def test_create_platform_product(self):
        # given
        platform_product_fixture = self.fixtures.platform_product
        create_data = platform_product_fixture.to_json()
        create_data = {k: create_data[k] for k in [field.name for field in fields(PlatformProductCreate)]}

        # when
        created_platform_product = self.models.platform_products.create(PlatformProductCreate(**create_data))
        self.addCleanup(lambda: self.factory.platform_products.cleanup(created_platform_product._id))

        # then
        self.assertIsNotNone(created_platform_product)
        self.assertEqual(created_platform_product.platform_id, platform_product_fixture.platform_id)

    def test_patch_platform_product(self):
        platform_products_model = PlatformProductsModel(self.services.db)

        # given
        patch_data = PlatformProductPatch(platform_id=12345)
        fixture = self.fixtures.platform_product.clone()
        platform_product_fixture, cleanup = self.factory.platform_products.create(fixture)
        self.addCleanup(cleanup)

        # when
        updated_platform_product = platform_products_model.patch(str(platform_product_fixture._id), patch_data)

        # then
        self.assertIsNotNone(updated_platform_product)
        self.assertEqual(updated_platform_product.platform_id, 12345)

    def test_delete_platform_product(self):
        platform_products_model = PlatformProductsModel(self.services.db)

        # given
        platform_product_fixture, cleanup = self.factory.platform_products.create(
            self.fixtures.platform_product.clone())
        self.addCleanup(cleanup)

        # when
        deleted_platform_product = platform_products_model.delete(str(platform_product_fixture._id))
        retrieved_platform_product_after_deletion = platform_products_model.get(str(platform_product_fixture._id))

        # then
        self.assertIsNotNone(deleted_platform_product)
        self.assertEqual(deleted_platform_product.platform_id, platform_product_fixture.platform_id)
        self.assertIsNone(retrieved_platform_product_after_deletion)
