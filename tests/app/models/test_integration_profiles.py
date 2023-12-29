from app.main import app
from app.models.profiles import ProfilesModel, ProfilePatch, ProfileCreate
from tests.integration_test import IntegrationTest


class ProfilesModelTestCase(IntegrationTest):

    def test_get_profile(self):
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)

        # given
        factory = self.factory.profiles
        test_profile, cleanup = factory.create(ProfileCreate(email="test.pork@pork.com", password="JohnPork2003"))
        self.addCleanup(cleanup)

        # when
        retrieved_profile = profiles_model.get(str(test_profile._id))

        # then
        self.assertIsNotNone(test_profile._id)
        self.assertEqual(test_profile._id, retrieved_profile._id)
        self.assertEqual(test_profile.email, retrieved_profile.email)

    def test_patch_profile(self):
        # TODO: implement patch profile method in model
        self.skipTest("Not implemented PATCH method in ProfilesModel")
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)

        # given
        factory = self.factory.profiles
        test_profile, cleanup = factory.create(ProfileCreate(email="test.pork@pork.com", password="JohnPork2003"))
        self.addCleanup(cleanup)
        patch_data = ProfilePatch(email="updated@example.com")

        # when
        with self.assertRaises(Exception) as context:
            profiles_model.patch(str(test_profile._id), patch_data)

        # then
        self.assertIn("Not implemented.", str(context.exception))

    def test_delete_profile(self):
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)

        # given
        factory = self.factory.profiles
        test_profile, cleanup = factory.create(ProfileCreate(email="test.pork@pork.com", password="JohnPork2003"))
        self.addCleanup(cleanup)

        # when
        deleted_profile = profiles_model.delete(str(test_profile._id))
        retrieved_profile_after_deletion = profiles_model.get(str(test_profile._id))

        # then
        self.assertIsNotNone(deleted_profile)
        self.assertEqual(deleted_profile._id, test_profile._id)
        self.assertIsNone(retrieved_profile_after_deletion)
