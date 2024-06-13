from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from datetime import datetime

from app.models.exceptions import NotFoundException
from app.models.game_guesses import GameGuessesModel, GameGuessCreate, GameGuess, GameGuessPatch
from tests import UnitTest

# TODO: Create a separate fixtures entity for unit tests
game_guess_fixture = GameGuess(
    daily_guess_game_id=ObjectId(),
    ip="127.0.0.1",
    attempts=[{"product_id": "1234", "data": {"key": "value"}}]
)


class GameGuessTestCase(UnitTest):

    @patch("app.models.guess_games.Database")
    def test_create_game_guess(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_a_game_guess():
            # given
            model = GameGuessesModel(db)
            mock_game_guess = game_guess_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = GameGuessCreate(
                daily_guess_game_id=mock_game_guess.daily_guess_game_id,
                ip=mock_game_guess.ip,
                attempts=mock_game_guess.attempts,
                profile_id=mock_game_guess.profile_id,
                guessed_at=mock_game_guess.guessed_at
            )

            expected_result = mock_game_guess

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.daily_guess_game_id, expected_result.daily_guess_game_id)
            self.assertEqual(result.ip, expected_result.ip)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_game_guess
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_get_game_guess(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_game_guess():
            # given
            model = GameGuessesModel(db)
            game_guess_id = ObjectId()
            mock_game_guess = game_guess_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_game_guess.to_json()

            # when
            result = model.get(str(game_guess_id))

            # then
            self.assertEqual(result.daily_guess_game_id, mock_game_guess.daily_guess_game_id)
            collection_mock.find_one.assert_called_once_with({'_id': game_guess_id})

        def fails_to_get_game_guess_because_id_is_invalid():
            # given
            model = GameGuessesModel(db)
            invalid_game_guess_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_game_guess_id)

        def fails_to_get_a_nonexistent_game_guess():
            # given
            model = GameGuessesModel(db)
            nonexistent_game_guess_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_game_guess_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_game_guess_id})

        tests = [
            gets_and_returns_game_guess,
            fails_to_get_game_guess_because_id_is_invalid,
            fails_to_get_a_nonexistent_game_guess
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_patch_game_guess(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_game_guess():
            # given
            model = GameGuessesModel(db)
            game_guess_id = ObjectId()
            updated_game_guess = game_guess_fixture.clone()
            updated_game_guess.attempts = [{"product_id": "1234", "data": {"key": "updated_value"}}]
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_game_guess.to_json()

            update_data = GameGuessPatch(
                attempts=[{"product_id": "1234", "data": {"key": "updated_value"}}]
            )

            # when
            result = model.patch(str(game_guess_id), update_data)

            # then
            self.assertEqual(result.attempts, updated_game_guess.attempts)

        def fails_to_patch_a_game_guess_because_id_is_invalid():
            # given
            model = GameGuessesModel(db)
            invalid_game_guess_id = "invalid_id"
            update_data = game_guess_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_game_guess_id, update_data)

        def fails_to_patch_a_nonexistent_game_guess():
            # given
            model = GameGuessesModel(db)
            nonexistent_game_guess_id = ObjectId()
            update_data = game_guess_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_game_guess_id), update_data)

        tests = [
            patches_and_returns_updated_game_guess,
            fails_to_patch_a_game_guess_because_id_is_invalid,
            fails_to_patch_a_nonexistent_game_guess
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_delete_game_guess(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = GameGuessesModel(db)
            game_guess_id = ObjectId()
            mock_game_guess = game_guess_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_game_guess.to_json()

            # when
            result = model.delete(str(game_guess_id))

            # then
            self.assertEqual(result.attempts, mock_game_guess.attempts)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': game_guess_id})

        def fails_to_delete_a_game_guess_because_id_is_invalid():
            # given
            model = GameGuessesModel(db)
            invalid_game_guess_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_game_guess_id)

        def fails_to_delete_a_nonexistent_game_guess():
            # given
            model = GameGuessesModel(db)
            nonexistent_game_guess_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_game_guess_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_game_guess_because_id_is_invalid,
            fails_to_delete_a_nonexistent_game_guess
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

