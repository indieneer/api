from bson import ObjectId

from app.models.product_replies import ProductRepliesModel, ProductReplyPatch, ProductReplyCreate
from tests.integration_test import IntegrationTest


class ProductReplyModelTestCase(IntegrationTest):

    def test_get_product_reply(self):
        product_reply_model = ProductRepliesModel(self.services.db)

        # given
        product_reply = self.fixtures.product_reply

        # when
        retrieved_product_reply = product_reply_model.get(str(product_reply._id))

        # then
        self.assertIsNotNone(retrieved_product_reply)
        self.assertEqual(product_reply.text, retrieved_product_reply.text)

    def test_create_product_reply(self):
        # given
        profile_fixture = self.fixtures.regular_user
        product_fixture = self.fixtures.product
        test_text = "Test integration models"

        # when
        created_product_reply = self.models.product_replies.create(ProductReplyCreate(comment_id=product_fixture._id, profile_id=profile_fixture._id, text=test_text))
        self.addCleanup(lambda: self.factory.product_replies.cleanup(created_product_reply._id))

        # then
        self.assertIsNotNone(created_product_reply)
        self.assertEqual(created_product_reply.text, test_text)

    def test_patch_product_reply(self):
        product_reply_model = ProductRepliesModel(self.services.db)

        # given
        product_reply = self.fixtures.product_reply.clone()
        patch_data = ProductReplyPatch(text="Updated product reply text")

        created_product_reply, cleanup = self.factory.product_replies.create(product_reply)
        self.addCleanup(cleanup)

        # when
        updated_product_reply = product_reply_model.patch(str(created_product_reply._id), patch_data)

        # then
        self.assertIsNotNone(updated_product_reply)
        self.assertEqual(updated_product_reply.text, "Updated product reply text")

    def test_delete_product_reply(self):
        product_reply_model = ProductRepliesModel(self.services.db)

        # given
        product_reply, cleanup = self.factory.product_replies.create(self.fixtures.product_reply.clone())
        self.addCleanup(cleanup)

        # when
        self.models.product_replies.delete(product_reply._id)
        retrieved_product_reply_after_deletion = product_reply_model.get(product_reply._id)

        # then
        self.assertIsNone(retrieved_product_reply_after_deletion)

    def test_get_all_product_replies(self):
        # given
        product_reply_model = ProductRepliesModel(self.services.db)
        product_reply, cleanup = self.factory.product_replies.create(self.fixtures.product_reply.clone())
        self.addCleanup(cleanup)
        comment_id = product_reply.comment_id

        # when
        all_product_replies = product_reply_model.get_all(comment_id)

        # then
        self.assertIsNotNone(all_product_replies)
        self.assertIn(product_reply, all_product_replies)
        self.assertGreater(len(all_product_replies), 0)
