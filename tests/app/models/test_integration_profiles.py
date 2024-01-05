import time

from bson import ObjectId

from app.models.profiles import ProfilesModel, ProfileCreate
from tests.integration_test import IntegrationTest


class ProfilesModelTestCase(IntegrationTest):
    def test_get_profile(self):
        # given
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)
        test_profile, cleanup = self.factory.profiles.create(
            ProfileCreate(email="test.pork@pork.com", password="JohnPork2003"))
        self.addCleanup(cleanup)

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        retrieved_profile = profiles_model.get(str(test_profile._id))

        # then
        self.assertIsNotNone(test_profile._id)
        self.assertEqual(test_profile._id, retrieved_profile._id)
        self.assertEqual(test_profile.email, retrieved_profile.email)

    def test_get_profile_not_found(self):
        # given
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        retrieved_profile = profiles_model.get(str(ObjectId()))

        # then
        self.assertIsNone(retrieved_profile)

    def test_find_by_email(self):
        # given
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)
        test_profile, cleanup = self.factory.profiles.create(
            ProfileCreate(email="test.pork@pork.com", password="JohnPork2003"))
        self.addCleanup(cleanup)

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        retrieved_profile = profiles_model.get(str(test_profile._id))

        # then
        self.assertIsNotNone(test_profile._id)
        self.assertEqual(test_profile._id, retrieved_profile._id)
        self.assertEqual(test_profile.email, retrieved_profile.email)

    def test_create_profile(self):
        # given
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)
        profile_create = ProfileCreate(
            email="test.pork@pork.com", password="JohnPork2003"
        )

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        created_profile = profiles_model.create(profile_create)

        # then
        self.factory.profiles.cleanup(profile_create.email)
        self.assertIsNotNone(created_profile)
        self.assertEqual(created_profile.email, profile_create.email)

    def test_patch_profile(self):
        # TODO: implement patch profile method in model
        self.skipTest("Not implemented PATCH method in ProfilesModel")

    def test_delete_profile(self):
        # given
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)
        test_profile, cleanup = self.factory.profiles.create(
            ProfileCreate(email="test.pork@pork.com", password="JohnPork2003"))
        self.addCleanup(cleanup)

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        deleted_profile = profiles_model.delete(str(test_profile._id))
        retrieved_profile_after_deletion = profiles_model.get(str(test_profile._id))

        # then
        self.assertIsNotNone(deleted_profile)
        self.assertEqual(deleted_profile._id, test_profile._id)
        self.assertIsNone(retrieved_profile_after_deletion)
