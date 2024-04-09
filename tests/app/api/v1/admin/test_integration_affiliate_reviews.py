from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.affiliate_reviews import AffiliateReviewCreate


class AffiliateReviewTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_create_affiliate_review(self):
        # given
        payload = {
            "profile_id": str(ObjectId()),
            "affiliate_id": str(ObjectId()),
            "affiliate_platform_product_id": str(ObjectId()),
            "text": "Excellent product!",
            "rating": 5
        }

        # when
        response = self.app.post("/v1/admin/affiliate_reviews", headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["text"], "Excellent product!")
        created_review_id = response_json["data"]["_id"]
        self.addCleanup(lambda: self.app.delete(f"/v1/admin/affiliate_reviews/{created_review_id}", headers={"Authorization": f'Bearer {self.token}'}))

    def test_get_affiliate_review_by_id(self):
        # Preparing a review to get
        created_review, cleanup = self.factory.affiliate_reviews.create(AffiliateReviewCreate(
            profile_id=ObjectId(),
            affiliate_id=ObjectId(),
            affiliate_platform_product_id=ObjectId(),
            rating=5,
            text="Great product!"
        ))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/affiliate_reviews/{created_review._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["_id"], str(created_review._id))

    def test_update_affiliate_review(self):
        # Preparing a review to update
        created_review, cleanup = self.factory.affiliate_reviews.create(AffiliateReviewCreate(
            profile_id=ObjectId(),
            affiliate_id=ObjectId(),
            affiliate_platform_product_id=ObjectId(),
            rating=5,
            text="Initial review"
        ))
        self.addCleanup(cleanup)

        # given
        update_payload = {
            "text": "Updated review",
            "rating": 4
        }

        # when
        response = self.app.patch(f"/v1/admin/affiliate_reviews/{created_review._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["text"], "Updated review")
        self.assertEqual(response_json["data"]["rating"], 4)

    def test_delete_affiliate_review(self):
        # Preparing a review to delete
        created_review, cleanup = self.factory.affiliate_reviews.create(AffiliateReviewCreate(
            profile_id=ObjectId(),
            affiliate_id=ObjectId(),
            affiliate_platform_product_id=ObjectId(),
            rating=5,
            text="Review to delete"
        ))

        # when
        response = self.app.delete(f"/v1/admin/affiliate_reviews/{created_review._id}", headers={"Authorization": f'Bearer {self.token}'})

        # then
        self.assertEqual(response.status_code, 200)

        # Verifying deletion
        response = self.app.get(f"/v1/admin/affiliate_reviews/{created_review._id}", headers={"Authorization": f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 404)

    def test_get_all_affiliate_reviews(self):
        # when
        response = self.app.get("/v1/admin/affiliate_reviews", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response_json["data"], list)
