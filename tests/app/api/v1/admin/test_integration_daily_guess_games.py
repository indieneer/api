from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.daily_guess_games import DailyGuessGameCreate


class DailyGuessGameTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_daily_guess_games(self):
        # given
        daily_guess_game, cleanup = self.factory.daily_guess_games.create(DailyGuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "value"}, display_at="2036-02-03T00:00:00"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/daily_guess_games", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(daily_guess_game.to_json(), response_json["data"])

    def test_get_daily_guess_game_by_id(self):
        # given
        daily_guess_game, cleanup = self.factory.daily_guess_games.create(DailyGuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "specific_value"}, display_at="2036-02-03T00:00:00"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/daily_guess_games/{daily_guess_game._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["data"], {"key": "specific_value"})

    def test_create_daily_guess_game(self):
        # given
        payload = {
            "product_id": str(ObjectId()),
            "type": "attributes",
            "data": {"key": "new_value"},
            "display_at": "2036-02-03T00:00:00"
        }

        # when
        response = self.app.post("/v1/admin/daily_guess_games", headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()
        self.addCleanup(
            lambda: self.factory.daily_guess_games.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["data"], {"key": "new_value"})

    def test_update_daily_guess_game(self):
        # given
        daily_guess_game, cleanup = self.factory.daily_guess_games.create(DailyGuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "before_update"}, display_at="2036-02-03T00:00:00"))
        self.addCleanup(cleanup)
        update_payload = {"data": {"key": "after_update"}}

        # when
        response = self.app.patch(f"/v1/admin/daily_guess_games/{daily_guess_game._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["data"], {"key": "after_update"})

    def test_delete_daily_guess_game(self):
        # given
        daily_guess_game, cleanup = self.factory.daily_guess_games.create(DailyGuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "to_be_deleted"}, display_at="2036-02-03T00:00:00"))
        self.addCleanup(cleanup)

        # when
        response = self.app.delete(f"/v1/admin/daily_guess_games/{daily_guess_game._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Daily guess game {daily_guess_game._id} successfully deleted')