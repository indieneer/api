from bson import ObjectId

from app.models.profiles import ProfileCreate, ProfilesModel
from tests.integration_test import IntegrationTest


class ProfilesModelTestCase(IntegrationTest):

    def test_get(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        def finds_a_profile():
            # given
            fixture = self.fixtures.regular_user

            # when
            result = model.get(str(fixture._id))

            # then
            self.assertIsNotNone(result)
            self.assertEqual(result._id, fixture._id)

        def does_not_find_a_profile():
            # given
            mock_id = ObjectId()

            # when
            result = model.get(str(mock_id))

            # then
            self.assertIsNone(result)

        tests = [
            finds_a_profile,
            does_not_find_a_profile,
        ]

        self.run_subtests(tests)

    def test_find_by_email(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        def finds_a_profile():
            # given
            fixture = self.fixtures.regular_user

            # when
            result = model.get(str(fixture._id))

            # then
            self.assertIsNotNone(result)
            self.assertEqual(result._id, fixture._id)
            self.assertEqual(result.email, fixture.email)

        def does_not_find_a_profile():
            # given
            mock_email = "john.doe@nonexisting.com"

            # when
            result = model.find_by_email(mock_email)

            # then
            self.assertIsNone(result)

        tests = [
            finds_a_profile,
            does_not_find_a_profile,
        ]

        self.run_subtests(tests)

    def test_delete_db_profile(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        profile, cleanup = self.factory.profiles.create(ProfileCreate(
            display_name="John Doe",
            email="john.doe@gmail.com",
            nickname="john_doe",
            password="John_Doe@235"
        ))
        self.addCleanup(cleanup)

        def deletes_a_profile_and_returns_it():
            # when
            result = model.delete_db_profile(str(profile._id))

            # then
            self.assertIsNotNone(result)
            self.assertEqual(result._id, profile._id)

        def does_not_find_a_profile_and_returns_none():
            # when
            result = model.delete_db_profile(str(profile._id))

            # then
            self.assertIsNone(result)

        tests = [
            deletes_a_profile_and_returns_it,
            does_not_find_a_profile_and_returns_none
        ]

        self.run_subtests(tests)
