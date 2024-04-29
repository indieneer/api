from datetime import datetime
from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.affiliates import AffiliateCreate


class AffiliateTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_affiliates(self):
        # given
        affiliate, cleanup = self.factory.affiliates.create(AffiliateCreate(name="Test Affiliate", slug="test-affiliate", code="TESTCODE", became_seller_at=datetime.now(), sales=10, bio="Test Bio", enabled=True, logo_url="http://test.com/logo.png"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/affiliates", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(affiliate.to_json(), response_json["data"])

    def test_get_affiliate_by_id(self):
        # given
        affiliate, cleanup = self.factory.affiliates.create(AffiliateCreate(name="Specific Affiliate", slug="specific-affiliate", code="SPECIFIC", became_seller_at=datetime.now(), sales=20, bio="Specific Bio", enabled=True, logo_url="http://specific.com/logo.png"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/affiliates/{affiliate._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["name"], "Specific Affiliate")

    def test_create_affiliate(self):
        # given
        payload = {
            "name": "New Affiliate",
            "slug": "new-affiliate",
            "code": "NEW",
            "became_seller_at": datetime.now().isoformat(),
            "sales": 0,
            "bio": "New affiliate bio",
            "enabled": True,
            "logo_url": "http://new.com/logo.png"
        }

        # when
        response = self.app.post("/v1/admin/affiliates", headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()
        self.addCleanup(
            lambda: self.factory.affiliates.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["name"], "New Affiliate")

    def test_update_affiliate(self):
        # given
        affiliate, cleanup = self.factory.affiliates.create(AffiliateCreate(name="Update Test", slug="update-test", code="UPDATE", became_seller_at=datetime.now(), sales=30, bio="Before update", enabled=True, logo_url="http://update.com/logo.png"))
        self.addCleanup(cleanup)
        update_payload = {"bio": "After update"}

        # when
        response = self.app.patch(f"/v1/admin/affiliates/{affiliate._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["bio"], "After update")

    def test_delete_affiliate(self):
        # given
        affiliate, cleanup = self.factory.affiliates.create(AffiliateCreate(name="Delete Test", slug="delete-test", code="DELETE", became_seller_at=datetime.now(), sales=40, bio="To be deleted", enabled=True, logo_url="http://delete.com/logo.png"))
        self.addCleanup(cleanup)

        # when
        response = self.app.delete(f"/v1/admin/affiliates/{affiliate._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Affiliate {affiliate._id} successfully deleted')
