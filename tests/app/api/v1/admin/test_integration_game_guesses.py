from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.game_guesses import GameGuessCreate


class GameGuessTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_game_guesses(self):
        # given
        game_guess, cleanup = self.factory.game_guesses.create(GameGuessCreate(daily_guess_game_id=ObjectId(), ip="127.0.0.1", attempts=[{"product_id": "1234", "data": {"key": "value"}}]))
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/game_guesses", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(game_guess.to_json(), response_json["data"])

    def test_get_game_guess_by_id(self):
        # given
        game_guess, cleanup = self.factory.game_guesses.create(GameGuessCreate(daily_guess_game_id=ObjectId(), ip="127.0.0.1", attempts=[{"product_id": "1234", "data": {"key": "specific_value"}}]))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/game_guesses/{game_guess._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["attempts"], [{"product_id": "1234", "data": {"key": "specific_value"}}])

    def test_create_game_guess(self):
        # given
        payload = {
            "daily_guess_game_id": str(ObjectId()),
            "ip": "127.0.0.1",
            "attempts": [{"product_id": "1234", "data": {"key": "new_value"}}]
        }

        # when
        response = self.app.post("/v1/admin/game_guesses", headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()
        self.addCleanup(
            lambda: self.factory.game_guesses.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["attempts"], [{"product_id": "1234", "data": {"key": "new_value"}}])

    def test_update_game_guess(self):
        # given
        game_guess, cleanup = self.factory.game_guesses.create(GameGuessCreate(daily_guess_game_id=ObjectId(), ip="127.0.0.1", attempts=[{"product_id": "1234", "data": {"key": "before_update"}}]))
        self.addCleanup(cleanup)
        update_payload = {"attempts": [{"product_id": "1234", "data": {"key": "after_update"}}]}

        # when
        response = self.app.patch(f"/v1/admin/game_guesses/{game_guess._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["attempts"], [{"product_id": "1234", "data": {"key": "after_update"}}])

    def test_delete_game_guess(self):
        # given
        game_guess, cleanup = self.factory.game_guesses.create(GameGuessCreate(daily_guess_game_id=ObjectId(), ip="127.0.0.1", attempts=[{"product_id": "1234", "data": {"key": "to_be_deleted"}}]))
        self.addCleanup(cleanup)

        # when
        response = self.app.delete(f"/v1/admin/game_guesses/{game_guess._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Game guess {game_guess._id} successfully deleted')
