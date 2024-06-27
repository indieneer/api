from app.models.affiliate_reviews import AffiliateReviewsModel, AffiliateReviewPatch
from tests.integration_test import IntegrationTest


class AffiliateReviewsModelTestCase(IntegrationTest):
    def test_create_affiliate_review(self):
        # given
        affiliate_review = self.fixtures.affiliate_review.clone()

        # when
        created_review = self.models.affiliate_reviews.create(affiliate_review)
        self.addCleanup(lambda: self.factory.affiliate_reviews.cleanup(created_review._id))

        # then
        self.assertIsNotNone(created_review)
        self.assertEqual(created_review.rating, affiliate_review.rating)
        self.assertEqual(created_review.text, affiliate_review.text)

    def test_get_affiliate_review(self):
        # given
        created_review, cleanup = self.factory.affiliate_reviews.create(
            self.fixtures.affiliate_review.clone())
        self.addCleanup(cleanup)

        # when
        retrieved_review = self.models.affiliate_reviews.get(str(created_review._id))

        # then
        self.assertIsNotNone(retrieved_review)
        self.assertEqual(retrieved_review.rating, created_review.rating)

    def test_patch_affiliate_review(self):
        # given
        created_review, cleanup = self.factory.affiliate_reviews.create(
            self.fixtures.affiliate_review.clone())
        self.addCleanup(cleanup)
        patch_data = AffiliateReviewPatch(rating=4, text="Updated review")

        # when
        updated_review = self.models.affiliate_reviews.patch(str(created_review._id), patch_data)

        # then
        self.assertIsNotNone(updated_review)
        self.assertEqual(updated_review.rating, patch_data.rating)
        self.assertEqual(updated_review.text, patch_data.text)

    def test_delete_affiliate_review(self):
        # given
        created_review, cleanup = self.factory.affiliate_reviews.create(
            self.fixtures.affiliate_review.clone())

        # when
        self.models.affiliate_reviews.delete(created_review._id)
        retrieved_review_after_deletion = self.models.affiliate_reviews.get(str(created_review._id))

        # then
        self.assertIsNone(retrieved_review_after_deletion)
        cleanup()

    def test_get_all_affiliate_reviews(self):
        # when
        all_reviews = self.models.affiliate_reviews.get_all()

        # then
        self.assertIsNotNone(all_reviews)
        self.assertGreater(len(all_reviews), 0)
