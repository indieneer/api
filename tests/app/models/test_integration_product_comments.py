from bson import ObjectId

from app.models.product_comments import ProductCommentsModel, ProductCommentPatch, ProductCommentCreate
from tests.integration_test import IntegrationTest


class ProductCommentModelTestCase(IntegrationTest):

    def test_get_product_comment(self):
        product_comment_model = self.models.product_comments

        # given
        product_comment = self.fixtures.product_comment

        # when
        retrieved_product_comment = product_comment_model.get(str(product_comment._id))

        # then
        self.assertIsNotNone(retrieved_product_comment)
        self.assertEqual(product_comment.text, retrieved_product_comment.text)

    def test_create_product_comment(self):
        # given
        profile_fixture = self.fixtures.regular_user
        product_fixture = self.fixtures.product
        test_text = "Test integration models"

        # when
        created_product_comment = self.models.product_comments.create(ProductCommentCreate(product_id=product_fixture._id, profile_id=profile_fixture._id, text=test_text))
        self.addCleanup(lambda: self.factory.product_comments.cleanup(created_product_comment._id))

        # then
        self.assertIsNotNone(created_product_comment)
        self.assertEqual(created_product_comment.text, test_text)

    def test_patch_product_comment(self):
        product_comment_model = self.models.product_comments

        # given
        product_comment = self.fixtures.product_comment.clone()
        patch_data = ProductCommentPatch(text="Updated product comment text")

        created_product_comment, cleanup = self.factory.product_comments.create(product_comment)
        self.addCleanup(cleanup)

        # when
        updated_product_comment = product_comment_model.patch(str(created_product_comment._id), patch_data)

        # then
        self.assertIsNotNone(updated_product_comment)
        self.assertEqual(updated_product_comment.text, "Updated product comment text")

    def test_delete_product_comment(self):
        product_comment_model = self.models.product_comments

        # given
        product_comment, cleanup = self.factory.product_comments.create(self.fixtures.product_comment.clone())
        self.addCleanup(cleanup)

        # when
        self.models.product_comments.delete(product_comment._id)
        retrieved_product_comment_after_deletion = product_comment_model.get(product_comment._id)

        # then
        self.assertIsNone(retrieved_product_comment_after_deletion)

    def test_get_all_product_comments(self):
        # given
        product_comment_model = self.models.product_comments
        product_comment, cleanup = self.factory.product_comments.create(self.fixtures.product_comment.clone())
        self.addCleanup(cleanup)
        product_id = product_comment.product_id

        # when
        all_product_comments = product_comment_model.get_all(product_id)

        # then
        self.assertIsNotNone(all_product_comments)
        self.assertIn(product_comment, all_product_comments)
        self.assertGreater(len(all_product_comments), 0)
