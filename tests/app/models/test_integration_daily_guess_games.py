from bson import ObjectId

from app.models.daily_guess_games import DailyGuessGamePatch, DailyGuessGameCreate
from tests.integration_test import IntegrationTest


class DailyGuessGameModelTestCase(IntegrationTest):

    def test_get_daily_guess_game(self):
        daily_guess_game_model = self.models.daily_guess_games

        # given
        daily_guess_game = self.fixtures.daily_guess_game

        # when
        retrieved_daily_guess_game = daily_guess_game_model.get(str(daily_guess_game._id))

        # then
        self.assertIsNotNone(retrieved_daily_guess_game)
        self.assertEqual(daily_guess_game.data, retrieved_daily_guess_game.data)

    def test_create_daily_guess_game(self):
        # given
        product_fixture = self.fixtures.product
        test_data = {"key": "value"}

        # when
        created_daily_guess_game = self.models.daily_guess_games.create(DailyGuessGameCreate(product_id=product_fixture._id, type="attributes", data=test_data, display_at="2036-02-03T00:00:00"))
        self.addCleanup(lambda: self.factory.daily_guess_games.cleanup(created_daily_guess_game._id))

        # then
        self.assertIsNotNone(created_daily_guess_game)
        self.assertEqual(created_daily_guess_game.data, test_data)

    def test_patch_daily_guess_game(self):
        daily_guess_game_model = self.models.daily_guess_games

        # given
        daily_guess_game = self.fixtures.daily_guess_game.clone()
        patch_data = DailyGuessGamePatch(data={"key": "updated_value"})

        created_daily_guess_game, cleanup = self.factory.daily_guess_games.create(daily_guess_game)
        self.addCleanup(cleanup)

        # when
        updated_daily_guess_game = daily_guess_game_model.patch(str(created_daily_guess_game._id), patch_data)

        # then
        self.assertIsNotNone(updated_daily_guess_game)
        self.assertEqual(updated_daily_guess_game.data, {"key": "updated_value"})

    def test_delete_daily_guess_game(self):
        daily_guess_game_model = self.models.daily_guess_games

        # given
        daily_guess_game, cleanup = self.factory.daily_guess_games.create(self.fixtures.daily_guess_game.clone())
        self.addCleanup(cleanup)

        # when
        self.models.daily_guess_games.delete(daily_guess_game._id)
        retrieved_daily_guess_game_after_deletion = daily_guess_game_model.get(daily_guess_game._id)

        # then
        self.assertIsNone(retrieved_daily_guess_game_after_deletion)

    def test_get_all_daily_guess_games(self):
        # given
        daily_guess_game_model = self.models.daily_guess_games
        daily_guess_game, cleanup = self.factory.daily_guess_games.create(self.fixtures.daily_guess_game.clone())
        self.addCleanup(cleanup)

        # when
        all_daily_guess_games = daily_guess_game_model.get_all()

        # then
        self.assertIsNotNone(all_daily_guess_games)
        self.assertIn(daily_guess_game, all_daily_guess_games)
        self.assertGreater(len(all_daily_guess_games), 0)

