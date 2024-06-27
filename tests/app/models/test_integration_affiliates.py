from app.models.affiliates import AffiliatesModel, AffiliatePatch, AffiliateCreate
from tests.integration_test import IntegrationTest


class AffiliatesModelTestCase(IntegrationTest):
    def test_get_affiliate(self):
        affiliates_model = self.models.affiliates

        # given
        affiliate = self.fixtures.affiliate

        # when
        retrieved_affiliate = affiliates_model.get(str(affiliate._id))

        # then
        self.assertIsNotNone(retrieved_affiliate)
        self.assertEqual(affiliate.name, retrieved_affiliate.name)

    def test_create_affiliate(self):
        # given
        affiliate = self.fixtures.affiliate.clone()

        # when
        created_affiliate = self.models.affiliates.create(affiliate)
        self.addCleanup(lambda: self.factory.affiliates.cleanup(affiliate._id))

        # then
        self.assertIsNotNone(created_affiliate)
        self.assertEqual(created_affiliate.name, affiliate.name)
        self.assertEqual(created_affiliate.bio, affiliate.bio)

    def test_patch_affiliate(self):
        affiliates_model = self.models.affiliates

        # given
        affiliate = self.fixtures.affiliate.clone()
        patch_data = AffiliatePatch(name="Updated Name")

        created_affiliate, cleanup = self.factory.affiliates.create(affiliate)
        self.addCleanup(cleanup)

        # when
        updated_affiliate = affiliates_model.patch(str(created_affiliate._id), patch_data)

        # then
        self.assertIsNotNone(updated_affiliate)
        self.assertEqual(updated_affiliate.name, "Updated Name")

    def test_delete_affiliate(self):
        affiliates_model = self.models.affiliates

        # given
        affiliate, cleanup = self.factory.affiliates.create(
            self.fixtures.affiliate.clone())
        self.addCleanup(cleanup)

        # when
        self.models.affiliates.delete(affiliate._id)
        retrieved_affiliate_after_deletion = affiliates_model.get(str(affiliate._id))

        # then
        self.assertIsNone(retrieved_affiliate_after_deletion)

    def test_get_all_affiliates(self):
        # given
        affiliates_model = self.models.affiliates

        # when
        all_affiliates = affiliates_model.get_all()

        # then
        self.assertIsNotNone(all_affiliates)
        self.assertGreater(len(all_affiliates), 0)
