from datetime import datetime
from bson import ObjectId

from lib import constants
from tests import IntegrationTest
from app.models.guess_games import GuessGameCreate


class GuessGameTestCase(IntegrationTest):
    @property
    def token(self):
        admin_user = self.fixtures.admin_user
        return self.factory.logins.login(admin_user.email, constants.strong_password).id_token

    def test_get_guess_games(self):
        # given
        guess_game, cleanup = self.factory.guess_games.create(GuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "value"}))
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/guess_games", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(guess_game.to_json(), response_json["data"])

    def test_get_guess_game_by_id(self):
        # given
        guess_game, cleanup = self.factory.guess_games.create(GuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "specific_value"}))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/guess_games/{guess_game._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["data"], {"key": "specific_value"})

    def test_create_guess_game(self):
        # given
        payload = {
            "product_id": str(ObjectId()),
            "type": "attributes",
            "data": {"key": "new_value"}
        }

        # when
        response = self.app.post("/v1/admin/guess_games", headers={"Authorization": f'Bearer {self.token}'}, json=payload)
        response_json = response.get_json()
        self.addCleanup(
            lambda: self.factory.guess_games.cleanup(ObjectId(response_json["data"]["_id"])))

        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["data"], {"key": "new_value"})

    def test_update_guess_game(self):
        # given
        guess_game, cleanup = self.factory.guess_games.create(GuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "before_update"}))
        self.addCleanup(cleanup)
        update_payload = {"data": {"key": "after_update"}}

        # when
        response = self.app.patch(f"/v1/admin/guess_games/{guess_game._id}", headers={"Authorization": f'Bearer {self.token}'}, json=update_payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["data"], {"key": "after_update"})

    def test_delete_guess_game(self):
        # given
        guess_game, cleanup = self.factory.guess_games.create(GuessGameCreate(product_id=ObjectId(), type="attributes", data={"key": "to_be_deleted"}))
        self.addCleanup(cleanup)

        # when
        response = self.app.delete(f"/v1/admin/guess_games/{guess_game._id}", headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["message"], f'Guess game {guess_game._id} successfully deleted')
