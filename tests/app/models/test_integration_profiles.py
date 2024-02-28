from bson import ObjectId

from app.models.profiles import ProfilesModel
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
