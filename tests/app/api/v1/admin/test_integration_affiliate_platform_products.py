from datetime import datetime
from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.affiliate_platform_products import AffiliatePlatformProductCreate


class AffiliatePlatformProductTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_affiliate_platform_products(self):
        # given
        data_fixture = self.fixtures.affiliate_platform_product.clone()
        affiliate_platform_product, cleanup = self.factory.affiliate_platform_products.create(data_fixture)
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/affiliate_platform_products", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(affiliate_platform_product.to_json(), response_json["data"])

    def test_get_affiliate_platform_product_by_id(self):
        # given
        data_fixture = self.fixtures.affiliate_platform_product.clone()
        affiliate_platform_product, cleanup = self.factory.affiliate_platform_products.create(data_fixture)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/affiliate_platform_products/{affiliate_platform_product._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["buy_page_url"], "https://www.example.com")

    def test_create_affiliate_platform_product(self):
        # given
        data_fixture = self.fixtures.affiliate_platform_product.clone()
        payload = data_fixture.to_dict()

        # TODO: create a `strip_metadata` reverse function, centralize metadata
        del payload["_id"]
        del payload["created_at"]
        del payload["updated_at"]

        # when
        response = self.app.post("/v1/admin/affiliate_platform_products", headers={"Authorization": f'Bearer {self.token}'}, json=AffiliatePlatformProductCreate(**payload).to_json())
        response_json = response.get_json()

        print(response_json)

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["buy_page_url"], payload["buy_page_url"])

    def test_update_affiliate_platform_product(self):
        # given
        data_fixture = self.fixtures.affiliate_platform_product.clone()
        affiliate_platform_product, cleanup = self.factory.affiliate_platform_products.create(data_fixture)
        self.addCleanup(cleanup)
        update_payload = {"buy_page_url": "https://www.example.com/new"}

        # when
        response = self.app.patch(f"/v1/admin/affiliate_platform_products/{affiliate_platform_product._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["buy_page_url"], "https://www.example.com/new")

    def test_delete_affiliate_platform_product(self):
        # given
        data_fixture = self.fixtures.affiliate_platform_product.clone()
        affiliate_platform_product, cleanup = self.factory.affiliate_platform_products.create(data_fixture)
        self.addCleanup(cleanup)
        # when
        response = self.app.delete(f"/v1/admin/affiliate_platform_products/{affiliate_platform_product._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Affiliate platform product {affiliate_platform_product._id} successfully deleted')
