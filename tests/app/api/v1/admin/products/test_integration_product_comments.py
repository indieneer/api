from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.product_comments import ProductCommentCreate


class ProductCommentTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_product_comments(self):
        # given
        data_fixture = self.fixtures.product_comment.clone()
        product_comment, cleanup = self.factory.product_comments.create(data_fixture)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/products/{product_comment.product_id}/comments", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(product_comment.to_json()["_id"], [item["_id"] for item in response_json["data"]])

    def test_get_product_comment_by_id(self):
        # given
        data_fixture = self.fixtures.product_comment.clone()
        product_comment, cleanup = self.factory.product_comments.create(data_fixture)
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/products/product_comments/{product_comment._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["text"], "Nice Game")

    def test_create_product_comment(self):
        # given
        data_fixture = self.fixtures.product_comment.clone()
        payload = data_fixture.to_json()

        # TODO: create a `strip_metadata` reverse function, centralize metadata
        del payload["_id"]
        del payload["created_at"]
        del payload["updated_at"]

        # when
        response = self.app.post(f'/v1/admin/products/product_comments', headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()

        self.addCleanup(lambda: self.factory.product_comments.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["text"], payload["text"])

    def test_update_product_comment(self):
        # given
        data_fixture = self.fixtures.product_comment.clone()
        product_comment, cleanup = self.factory.product_comments.create(data_fixture)
        self.addCleanup(cleanup)
        update_payload = {"text": "new"}

        # when
        response = self.app.patch(f"/v1/admin/products/product_comments/{product_comment._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["text"], "new")

    def test_delete_product_comment(self):
        # given
        data_fixture = self.fixtures.product_comment.clone()
        product_comment, cleanup = self.factory.product_comments.create(data_fixture)
        self.addCleanup(cleanup)
        # when
        response = self.app.delete(f"/v1/admin/products/product_comments/{product_comment._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Product comment {product_comment._id} successfully deleted')

    def test_get_product_comments_with_limit(self):
        # given
        data_fixture1 = self.fixtures.product_comment.clone()
        product_comment1, cleanup1 = self.factory.product_comments.create(data_fixture1)
        self.addCleanup(cleanup1)

        data_fixture2 = self.fixtures.product_comment.clone()
        product_comment2, cleanup2 = self.factory.product_comments.create(data_fixture2)
        self.addCleanup(cleanup2)

        # when
        limit = 1
        response = self.app.get(
            f"/v1/admin/products/{product_comment1.product_id}/comments?limit={limit}",
            headers={"Authorization": f'Bearer {self.token}'}
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response_json["data"]), limit)

    def test_get_product_comments_with_newest_first_true(self):
        # given
        data_fixture1 = self.fixtures.product_comment.clone()
        product_comment1, cleanup1 = self.factory.product_comments.create(data_fixture1)
        self.addCleanup(cleanup1)

        data_fixture2 = self.fixtures.product_comment.clone()
        product_comment2, cleanup2 = self.factory.product_comments.create(data_fixture2)
        self.addCleanup(cleanup2)

        # when
        response = self.app.get(
            f"/v1/admin/products/{product_comment1.product_id}/comments?newest_first=True",
            headers={"Authorization": f'Bearer {self.token}'}
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response_json["data"][0]["created_at"] >= response_json["data"][-1]["created_at"]
        )

    def test_get_product_comments_with_newest_first_false(self):
        # given
        data_fixture1 = self.fixtures.product_comment.clone()
        product_comment1, cleanup1 = self.factory.product_comments.create(data_fixture1)
        self.addCleanup(cleanup1)

        data_fixture2 = self.fixtures.product_comment.clone()
        product_comment2, cleanup2 = self.factory.product_comments.create(data_fixture2)
        self.addCleanup(cleanup2)

        # when
        response = self.app.get(
            f"/v1/admin/products/{product_comment1.product_id}/comments?newest_first=False",
            headers={"Authorization": f'Bearer {self.token}'}
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response_json["data"][0]["created_at"] <= response_json["data"][-1]["created_at"]
        )

    def test_get_product_comments_with_limit_and_newest_first(self):
        # given
        data_fixture1 = self.fixtures.product_comment.clone()
        product_comment1, cleanup1 = self.factory.product_comments.create(data_fixture1)
        self.addCleanup(cleanup1)

        data_fixture2 = self.fixtures.product_comment.clone()
        product_comment2, cleanup2 = self.factory.product_comments.create(data_fixture2)
        self.addCleanup(cleanup2)

        # when
        limit = 1
        response = self.app.get(
            f"/v1/admin/products/{product_comment1.product_id}/comments?limit={limit}&newest_first=True",
            headers={"Authorization": f'Bearer {self.token}'}
        )
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response_json["data"]), limit)
        self.assertTrue(
            response_json["data"][0]["created_at"] >= response_json["data"][-1]["created_at"]
        )
