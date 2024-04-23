from app.models.affiliate_platform_products import AffiliatePlatformProductsModel, AffiliatePlatformProductPatch, AffiliatePlatformProductCreate
from tests.integration_test import IntegrationTest


class AffiliatePlatformProductsModelTestCase(IntegrationTest):
    def test_get_affiliate_platform_product(self):
        affiliate_platform_products_model = AffiliatePlatformProductsModel(self.services.db)

        # given
        affiliate_platform_product = self.fixtures.affiliate_platform_product

        # when
        print(str(affiliate_platform_product._id))
        retrieved_affiliate_platform_product = affiliate_platform_products_model.get(str(affiliate_platform_product._id))

        # then
        self.assertIsNotNone(retrieved_affiliate_platform_product)
        self.assertEqual(affiliate_platform_product.buy_page_url, retrieved_affiliate_platform_product.buy_page_url)

    def test_create_affiliate_platform_product(self):
        # given
        affiliate_platform_product = self.fixtures.affiliate_platform_product.clone()

        # when
        created_affiliate_platform_product = self.models.affiliate_platform_products.create(affiliate_platform_product)
        self.addCleanup(lambda: self.factory.affiliate_platform_products.cleanup(affiliate_platform_product._id))

        # then
        self.assertIsNotNone(created_affiliate_platform_product)
        self.assertEqual(created_affiliate_platform_product.buy_page_url, affiliate_platform_product.buy_page_url)

    def test_patch_affiliate_platform_product(self):
        affiliate_platform_products_model = AffiliatePlatformProductsModel(self.services.db)

        # given
        affiliate_platform_product = self.fixtures.affiliate_platform_product.clone()
        patch_data = AffiliatePlatformProductPatch(buy_page_url="https://www.example.com/new")

        created_affiliate_platform_product, cleanup = self.factory.affiliate_platform_products.create(affiliate_platform_product)
        self.addCleanup(cleanup)

        # when
        updated_affiliate_platform_product = affiliate_platform_products_model.patch(str(created_affiliate_platform_product._id), patch_data)

        # then
        self.assertIsNotNone(updated_affiliate_platform_product)
        self.assertEqual(updated_affiliate_platform_product.buy_page_url, "https://www.example.com/new")

    def test_delete_affiliate_platform_product(self):
        affiliate_platform_products_model = AffiliatePlatformProductsModel(self.services.db)

        # given
        affiliate_platform_product, cleanup = self.factory.affiliate_platform_products.create(
            self.fixtures.affiliate_platform_product.clone())
        self.addCleanup(cleanup)

        # when
        self.models.affiliate_platform_products.delete(affiliate_platform_product._id)
        retrieved_affiliate_platform_product_after_deletion = affiliate_platform_products_model.get(str(affiliate_platform_product._id))

        # then
        self.assertIsNone(retrieved_affiliate_platform_product_after_deletion)

    def test_get_all_affiliate_platform_products(self):
        # given
        affiliate_platform_products_model = AffiliatePlatformProductsModel(self.services.db)

        # when
        all_affiliate_platform_products = affiliate_platform_products_model.get_all()

        # then
        self.assertIsNotNone(all_affiliate_platform_products)
        self.assertGreater(len(all_affiliate_platform_products), 0)

