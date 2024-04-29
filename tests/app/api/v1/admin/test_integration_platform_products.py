from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.platform_products import PlatformProductCreate


class PlatformProductTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_platform_products(self):
        # given
        platform_product, cleanup = self.factory.platform_products.create(PlatformProductCreate(platform_id=1, prices=[], product_page_url="https://www.example.com/product"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/platform_products", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(platform_product.to_json(), response_json["data"])

    def test_get_platform_product_by_id(self):
        # given
        platform_product, cleanup = self.factory.platform_products.create(PlatformProductCreate(platform_id=2, prices=[], product_page_url="https://www.specific.com/product"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/platform_products/{platform_product._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["product_page_url"], "https://www.specific.com/product")

    def test_create_platform_product(self):
        # given
        payload = {
            "platform_id": 3,
            "prices": [],
            "product_page_url": "https://www.new.com/product"
        }

        # when
        response = self.app.post("/v1/admin/platform_products", headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()
        self.addCleanup(
            lambda: self.factory.platform_products.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["product_page_url"], "https://www.new.com/product")

    def test_update_platform_product(self):
        # given
        platform_product, cleanup = self.factory.platform_products.create(PlatformProductCreate(platform_id=4, prices=[], product_page_url="https://www.update.com/product"))
        self.addCleanup(cleanup)
        update_payload = {"prices": [{"amount": 19.99, "currency": "USD"}]}

        # when
        response = self.app.patch(f"/v1/admin/platform_products/{platform_product._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["prices"], [{"amount": 19.99, "currency": "USD"}])

    def test_delete_platform_product(self):
        # given
        platform_product, cleanup = self.factory.platform_products.create(PlatformProductCreate(platform_id=5, prices=[], product_page_url="https://www.delete.com/product"))
        self.addCleanup(cleanup)

        # when
        response = self.app.delete(f"/v1/admin/platform_products/{platform_product._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Platform product {platform_product._id} successfully deleted')

