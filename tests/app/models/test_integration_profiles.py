import random

from app.main import app
from app.models.profiles import ProfilesModel, ProfilePatch, ProfileCreate
from tests.integration_test import IntegrationTest


class ProfilesModelTestCase(IntegrationTest):

    def test_get_profile(self):
        profiles_model = ProfilesModel(self.services.db, self.services.auth0)

        # given
        fixture = self.fixtures.regular_user

        # when
        retrieved_profile = profiles_model.get(str(fixture._id))

        # then
        self.assertIsNotNone(fixture._id)
        self.assertEqual(fixture._id, retrieved_profile._id)
        self.assertEqual(fixture.email, retrieved_profile.email)

    def test_create_profile(self):
        # given
        salt = ''.join(random.choices('0123456789', k=10))
        test_profile = self.models.profiles.create(ProfileCreate(email=f'{salt}test.pork@pork.com', password=f'JohnPork2003{salt}'))
        self.addCleanup(lambda: self.factory.profiles.cleanup(test_profile._id))

        self.assertEqual(test_profile.email, f'{salt}test.pork@pork.com')
        self.assertIn("auth0|", test_profile.idp_id)

    def test_patch_profile(self):
        # FIXME: Change this test after merging PR #42
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
