from app.models.comments import CommentsModel, CommentPatch, CommentCreate
from tests.integration_test import IntegrationTest


class CommentModelTestCase(IntegrationTest):

    def test_get_comment(self):
        comment_model = CommentsModel(self.services.db)

        # given
        comment = self.fixtures.comment

        # when
        retrieved_comment = comment_model.get(str(comment.product_id), str(comment._id))

        # then
        self.assertIsNotNone(retrieved_comment)
        self.assertEqual(comment.text, retrieved_comment.text)

    def test_create_comment(self):
        # given
        comment = self.fixtures.comment.clone()

        # when
        created_comment = self.models.comments.create(str(comment.product_id), comment)
        self.addCleanup(lambda: self.factory.comments.cleanup(comment._id))

        # then
        self.assertIsNotNone(created_comment)
        self.assertEqual(created_comment.text, comment.text)

    def test_patch_comment(self):
        comment_model = CommentsModel(self.services.db)

        # given
        comment = self.fixtures.comment.clone()
        patch_data = CommentPatch(text="Updated comment text")

        created_comment, cleanup = self.factory.comments.create(comment)
        self.addCleanup(cleanup)

        # when
        updated_comment = comment_model.patch(str(comment.product_id), str(created_comment._id), patch_data)

        # then
        self.assertIsNotNone(updated_comment)
        self.assertEqual(updated_comment.text, "Updated comment text")

    def test_delete_comment(self):
        comment_model = CommentsModel(self.services.db)

        # given
        comment, cleanup = self.factory.comments.create(self.fixtures.comment.clone())
        self.addCleanup(cleanup)

        # when
        self.models.comments.delete(str(comment.product_id), comment._id)
        retrieved_comment_after_deletion = comment_model.get(str(comment.product_id), str(comment._id))

        # then
        self.assertIsNone(retrieved_comment_after_deletion)

    def test_get_all_comments(self):
        # given
        comment_model = CommentsModel(self.services.db)
        product_id = self.factory.comments.create(self.fixtures.comment.clone())[0].product_id

        # when
        all_comments = comment_model.get_all(product_id)

        # then
        self.assertIsNotNone(all_comments)
        self.assertGreater(len(all_comments), 0)
