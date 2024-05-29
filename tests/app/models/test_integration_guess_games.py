from bson import ObjectId

from app.models.guess_games import GuessGamePatch, GuessGameCreate
from tests.integration_test import IntegrationTest


class GuessGameModelTestCase(IntegrationTest):

    def test_get_guess_game(self):
        guess_game_model = self.models.guess_games

        # given
        guess_game = self.fixtures.guess_game

        # when
        retrieved_guess_game = guess_game_model.get(str(guess_game._id))

        # then
        self.assertIsNotNone(retrieved_guess_game)
        self.assertEqual(guess_game.data, retrieved_guess_game.data)

    def test_create_guess_game(self):
        # given
        product_fixture = self.fixtures.product
        test_data = {"key": "value"}

        # when
        created_guess_game = self.models.guess_games.create(GuessGameCreate(product_id=product_fixture._id, type="attributes", data=test_data))
        self.addCleanup(lambda: self.factory.guess_games.cleanup(created_guess_game._id))

        # then
        self.assertIsNotNone(created_guess_game)
        self.assertEqual(created_guess_game.data, test_data)

    def test_patch_guess_game(self):
        guess_game_model = self.models.guess_games

        # given
        guess_game = self.fixtures.guess_game.clone()
        patch_data = GuessGamePatch(data={"key": "updated_value"})

        created_guess_game, cleanup = self.factory.guess_games.create(guess_game)
        self.addCleanup(cleanup)

        # when
        updated_guess_game = guess_game_model.patch(str(created_guess_game._id), patch_data)

        # then
        self.assertIsNotNone(updated_guess_game)
        self.assertEqual(updated_guess_game.data, {"key": "updated_value"})

    def test_delete_guess_game(self):
        guess_game_model = self.models.guess_games

        # given
        guess_game, cleanup = self.factory.guess_games.create(self.fixtures.guess_game.clone())
        self.addCleanup(cleanup)

        # when
        self.models.guess_games.delete(guess_game._id)
        retrieved_guess_game_after_deletion = guess_game_model.get(guess_game._id)

        # then
        self.assertIsNone(retrieved_guess_game_after_deletion)

    def test_get_all_guess_games(self):
        # given
        guess_game_model = self.models.guess_games
        guess_game, cleanup = self.factory.guess_games.create(self.fixtures.guess_game.clone())
        self.addCleanup(cleanup)
        product_id = guess_game.product_id

        # when
        all_guess_games = guess_game_model.get_all()

        # then
        self.assertIsNotNone(all_guess_games)
        self.assertIn(guess_game, all_guess_games)
        self.assertGreater(len(all_guess_games), 0)
