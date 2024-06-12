from bson import ObjectId

from app.models.game_guesses import GameGuessPatch, GameGuessCreate
from tests.integration_test import IntegrationTest


class GameGuessModelTestCase(IntegrationTest):

    def test_get_game_guess(self):
        game_guess_model = self.models.game_guesses

        # given
        game_guess = self.fixtures.game_guess

        # when
        retrieved_game_guess = game_guess_model.get(str(game_guess._id))

        # then
        self.assertIsNotNone(retrieved_game_guess)
        self.assertEqual(game_guess.attempts, retrieved_game_guess.attempts)

    def test_create_game_guess(self):
        # given
        daily_guess_game_fixture = self.fixtures.daily_guess_game
        test_attempts = [{"product_id": str(ObjectId()), "data": {"key": "value"}}]

        # when
        created_game_guess = self.models.game_guesses.create(GameGuessCreate(daily_guess_game_id=daily_guess_game_fixture._id, ip="127.0.0.1", attempts=test_attempts))
        self.addCleanup(lambda: self.factory.game_guesses.cleanup(created_game_guess._id))

        # then
        self.assertIsNotNone(created_game_guess)
        self.assertEqual(created_game_guess.attempts, test_attempts)

    def test_patch_game_guess(self):
        game_guess_model = self.models.game_guesses

        # given
        game_guess = self.fixtures.game_guess.clone()
        patch_data = GameGuessPatch(attempts=[{"product_id": (updated_id := str(ObjectId())), "data": {"key": "updated_value"}}])

        created_game_guess, cleanup = self.factory.game_guesses.create(game_guess)
        self.addCleanup(cleanup)

        # when
        updated_game_guess = game_guess_model.patch(str(created_game_guess._id), patch_data)

        # then
        self.assertIsNotNone(updated_game_guess)
        self.assertEqual(updated_game_guess.attempts, [{"product_id": updated_id, "data": {"key": "updated_value"}}])

    def test_delete_game_guess(self):
        game_guess_model = self.models.game_guesses

        # given
        game_guess, cleanup = self.factory.game_guesses.create(self.fixtures.game_guess.clone())
        self.addCleanup(cleanup)

        # when
        self.models.game_guesses.delete(game_guess._id)
        retrieved_game_guess_after_deletion = game_guess_model.get(game_guess._id)

        # then
        self.assertIsNone(retrieved_game_guess_after_deletion)

    def test_get_all_game_guesses(self):
        # given
        game_guess_model = self.models.game_guesses
        game_guess, cleanup = self.factory.game_guesses.create(self.fixtures.game_guess.clone())
        self.addCleanup(cleanup)

        # when
        all_game_guesses = game_guess_model.get_all()

        # then
        self.assertIsNotNone(all_game_guesses)
        self.assertIn(game_guess, all_game_guesses)
        self.assertGreater(len(all_game_guesses), 0)
