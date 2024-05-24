from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.product_replies import ProductReplyCreate


class ProductReplyTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_product_replies(self):
        # given
        data_fixture = self.fixtures.product_reply.clone()
        product_reply, cleanup = self.factory.product_replies.create(data_fixture)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/comments/{product_reply.comment_id}/product_replies", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(product_reply.to_json()["_id"], [item["_id"] for item in response_json["data"]])

    def test_get_product_reply_by_id(self):
        # given
        data_fixture = self.fixtures.product_reply.clone()
        product_reply, cleanup = self.factory.product_replies.create(data_fixture)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/comments/{product_reply.comment_id}/product_replies/{product_reply._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["text"], "I agree with you")

    def test_create_product_reply(self):
        # given
        data_fixture = self.fixtures.product_reply.clone()
        payload = data_fixture.to_json()

        # TODO: create a `strip_metadata` reverse function, centralize metadata
        del payload["_id"]
        del payload["created_at"]
        del payload["updated_at"]
        del payload["comment_id"]

        # when
        response = self.app.post(f'/v1/admin/comments/{data_fixture.comment_id}/product_replies', headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()
        self.addCleanup(lambda: self.factory.product_replies.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["text"], payload["text"])

    def test_update_product_reply(self):
        # given
        data_fixture = self.fixtures.product_reply.clone()
        product_reply, cleanup = self.factory.product_replies.create(data_fixture)
        self.addCleanup(cleanup)
        update_payload = {"text": "new"}

        # when
        response = self.app.patch(f"/v1/admin/comments/{product_reply.comment_id}/product_replies/{product_reply._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["text"], "new")

    def test_delete_product_reply(self):
        # given
        data_fixture = self.fixtures.product_reply.clone()
        product_reply, cleanup = self.factory.product_replies.create(data_fixture)
        self.addCleanup(cleanup)
        # when
        response = self.app.delete(f"/v1/admin/comments/{product_reply.comment_id}/product_replies/{product_reply._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Product reply {product_reply._id} successfully deleted')

