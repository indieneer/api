from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify
import datetime

from app.models.exceptions import NotFoundException
from app.models.daily_guess_games import DailyGuessGamesModel, DailyGuessGameCreate, DailyGuessGame, DailyGuessGamePatch
from tests import UnitTest

# TODO: Create a separate fixtures entity for unit tests
daily_guess_game_fixture = DailyGuessGame(
    product_id=ObjectId(),
    type="attributes",
    data={"key": "value"},
    display_at="2036-02-03T00:00:00"
)


class DailyGuessGameTestCase(UnitTest):

    @patch("app.models.guess_games.Database")
    def test_create_daily_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_a_daily_guess_game():
            # given
            model = DailyGuessGamesModel(db)
            mock_daily_guess_game = daily_guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = DailyGuessGameCreate(
                product_id=mock_daily_guess_game.product_id,
                type=mock_daily_guess_game.type,
                data=mock_daily_guess_game.data,
                display_at=mock_daily_guess_game.display_at
            )

            expected_result = mock_daily_guess_game

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.product_id, expected_result.product_id)
            self.assertEqual(result.type, expected_result.type)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_daily_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_get_daily_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_daily_guess_game():
            # given
            model = DailyGuessGamesModel(db)
            daily_guess_game_id = ObjectId()
            mock_daily_guess_game = daily_guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_daily_guess_game.to_json()

            # when
            result = model.get(str(daily_guess_game_id))

            # then
            self.assertEqual(result.product_id, mock_daily_guess_game.product_id)
            collection_mock.find_one.assert_called_once_with({'_id': daily_guess_game_id})

        def fails_to_get_daily_guess_game_because_id_is_invalid():
            # given
            model = DailyGuessGamesModel(db)
            invalid_daily_guess_game_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_daily_guess_game_id)

        def fails_to_get_a_nonexistent_daily_guess_game():
            # given
            model = DailyGuessGamesModel(db)
            nonexistent_daily_guess_game_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_daily_guess_game_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_daily_guess_game_id})

        tests = [
            gets_and_returns_daily_guess_game,
            fails_to_get_daily_guess_game_because_id_is_invalid,
            fails_to_get_a_nonexistent_daily_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_patch_daily_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_daily_guess_game():
            # given
            model = DailyGuessGamesModel(db)
            daily_guess_game_id = ObjectId()
            updated_daily_guess_game = daily_guess_game_fixture.clone()
            updated_daily_guess_game.data = {"key": "updated_value"}
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_daily_guess_game.to_json()

            update_data = DailyGuessGamePatch(
                data={"key": "updated_value"}
            )

            # when
            result = model.patch(str(daily_guess_game_id), update_data)

            # then
            self.assertEqual(result.data, updated_daily_guess_game.data)

        def fails_to_patch_a_daily_guess_game_because_id_is_invalid():
            # given
            model = DailyGuessGamesModel(db)
            invalid_daily_guess_game_id = "invalid_id"
            update_data = daily_guess_game_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_daily_guess_game_id, update_data)

        def fails_to_patch_a_nonexistent_daily_guess_game():
            # given
            model = DailyGuessGamesModel(db)
            nonexistent_daily_guess_game_id = ObjectId()
            update_data = daily_guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_daily_guess_game_id), update_data)

        tests = [
            patches_and_returns_updated_daily_guess_game,
            fails_to_patch_a_daily_guess_game_because_id_is_invalid,
            fails_to_patch_a_nonexistent_daily_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_delete_daily_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = DailyGuessGamesModel(db)
            daily_guess_game_id = ObjectId()
            mock_daily_guess_game = daily_guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_daily_guess_game.to_json()

            # when
            result = model.delete(str(daily_guess_game_id))

            # then
            self.assertEqual(result.data, mock_daily_guess_game.data)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': daily_guess_game_id})

        def fails_to_delete_a_daily_guess_game_because_id_is_invalid():
            # given
            model = DailyGuessGamesModel(db)
            invalid_daily_guess_game_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_daily_guess_game_id)

        def fails_to_delete_a_nonexistent_daily_guess_game():
            # given
            model = DailyGuessGamesModel(db)
            nonexistent_daily_guess_game_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_daily_guess_game_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_daily_guess_game_because_id_is_invalid,
            fails_to_delete_a_nonexistent_daily_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)
