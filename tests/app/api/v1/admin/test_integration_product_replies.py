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

    def test_does_not_find_a_reply_with_nonexistent_id(self):
        # given
        nonexistent_reply_id = ObjectId()
        existing_comment_id = self.fixtures.product_comment._id

        # when
        response = self.app.get(f"/v1/admin/comments/{existing_comment_id}/product_replies/{nonexistent_reply_id}",
                                headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json["error"], f'Product reply with ID {nonexistent_reply_id} not found')

    def test_comment_for_reply_not_found(self):
        # given
        nonexistent_comment_id = ObjectId()
        product_reply_id = ObjectId()  # Simulate any ObjectId for the product reply

        # when
        response = self.app.get(f"/v1/admin/comments/{nonexistent_comment_id}/product_replies/{product_reply_id}",
                                headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json["error"], f'The reply is attached to a nonexistent comment with ID {nonexistent_comment_id}')

    def test_create_product_reply(self):
        # given
        some_comment_id = str(ObjectId())
        payload = {
            "profile_id": str(ObjectId()),
            "text": "I agree with you"
        }

        # when
        response = self.app.post(f'/v1/admin/comments/{some_comment_id}/product_replies', headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()

        self.addCleanup(lambda: self.factory.product_replies.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["text"], payload["text"])

    def test_does_not_allow_to_create_a_reply_with_zero_length(self):
        # given
        some_comment_id = str(ObjectId())
        payload = {
            "profile_id": str(ObjectId()),
            "text": ""
        }

        # when
        response = self.app.post(f'/v1/admin/comments/{some_comment_id}/product_replies',
                                 headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()

        print(response_json)

        # then
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response_json["error"])

    def test_does_not_allow_to_edit_a_reply_to_be_zero_length(self):
        # given
        data_fixture = self.fixtures.product_reply.clone()
        product_reply, cleanup = self.factory.product_replies.create(data_fixture)
        self.addCleanup(cleanup)
        update_payload = {"text": ""}

        # when
        response = self.app.patch(f"/v1/admin/comments/{product_reply.comment_id}/product_replies/{product_reply._id}",
                                  headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response_json["error"])

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

