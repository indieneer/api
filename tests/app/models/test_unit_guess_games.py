from unittest.mock import patch, MagicMock
import bson
from bson import ObjectId
from pymongo import ReturnDocument
from slugify import slugify
import datetime

from app.models.exceptions import NotFoundException
from app.models.guess_games import GuessGamesModel, GuessGameCreate, GuessGame, GuessGamePatch
from tests import UnitTest

# TODO: Create a separate fixtures entity for unit tests
guess_game_fixture = GuessGame(
    product_id=ObjectId(),
    type="attributes",
    data={"key": "value"}
)


class GuessGameTestCase(UnitTest):

    @patch("app.models.guess_games.Database")
    def test_create_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def creates_and_returns_a_guess_game():
            # given
            model = GuessGamesModel(db)
            mock_guess_game = guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            expected_input = GuessGameCreate(
                product_id=mock_guess_game.product_id,
                type=mock_guess_game.type,
                data=mock_guess_game.data
            )

            expected_result = mock_guess_game

            # when
            result = model.create(input_data=expected_input)

            # then
            self.assertEqual(result.product_id, expected_result.product_id)
            self.assertEqual(result.type, expected_result.type)
            collection_mock.insert_one.assert_called_once()

        tests = [
            creates_and_returns_a_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_get_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def gets_and_returns_guess_game():
            # given
            model = GuessGamesModel(db)
            guess_game_id = ObjectId()
            mock_guess_game = guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = mock_guess_game.to_json()

            # when
            result = model.get(str(guess_game_id))

            # then
            self.assertEqual(result.product_id, mock_guess_game.product_id)
            collection_mock.find_one.assert_called_once_with({'_id': guess_game_id})

        def fails_to_get_guess_game_because_id_is_invalid():
            # given
            model = GuessGamesModel(db)
            invalid_guess_game_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.get(invalid_guess_game_id)

        def fails_to_get_a_nonexistent_guess_game():
            # given
            model = GuessGamesModel(db)
            nonexistent_guess_game_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one.return_value = None

            # when
            result = model.get(str(nonexistent_guess_game_id))

            # then
            self.assertIsNone(result)
            collection_mock.find_one.assert_called_once_with({'_id': nonexistent_guess_game_id})

        tests = [
            gets_and_returns_guess_game,
            fails_to_get_guess_game_because_id_is_invalid,
            fails_to_get_a_nonexistent_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_patch_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def patches_and_returns_updated_guess_game():
            # given
            model = GuessGamesModel(db)
            guess_game_id = ObjectId()
            updated_guess_game = guess_game_fixture.clone()
            updated_guess_game.data = {"key": "updated_value"}
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock

            collection_mock.find_one_and_update.return_value = updated_guess_game.to_json()

            update_data = GuessGamePatch(
                data={"key": "updated_value"}
            )

            # when
            result = model.patch(str(guess_game_id), update_data)

            # then
            self.assertEqual(result.data, updated_guess_game.data)

        def fails_to_patch_a_guess_game_because_id_is_invalid():
            # given
            model = GuessGamesModel(db)
            invalid_guess_game_id = "invalid_id"
            update_data = guess_game_fixture.clone()

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.patch(invalid_guess_game_id, update_data)

        def fails_to_patch_a_nonexistent_guess_game():
            # given
            model = GuessGamesModel(db)
            nonexistent_guess_game_id = ObjectId()
            update_data = guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_update.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.patch(str(nonexistent_guess_game_id), update_data)

        tests = [
            patches_and_returns_updated_guess_game,
            fails_to_patch_a_guess_game_because_id_is_invalid,
            fails_to_patch_a_nonexistent_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)

    @patch("app.models.guess_games.Database")
    def test_delete_guess_game(self, db: MagicMock):
        db_connection_mock = db.connection

        def deletes_and_confirms_deletion():
            # given
            model = GuessGamesModel(db)
            guess_game_id = ObjectId()
            mock_guess_game = guess_game_fixture.clone()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = mock_guess_game.to_json()

            # when
            result = model.delete(str(guess_game_id))

            # then
            self.assertEqual(result.data, mock_guess_game.data)
            collection_mock.find_one_and_delete.assert_called_once_with({'_id': guess_game_id})

        def fails_to_delete_a_guess_game_because_id_is_invalid():
            # given
            model = GuessGamesModel(db)
            invalid_guess_game_id = "invalid_id"

            # when & then
            with self.assertRaises(bson.errors.InvalidId):
                model.delete(invalid_guess_game_id)

        def fails_to_delete_a_nonexistent_guess_game():
            # given
            model = GuessGamesModel(db)
            nonexistent_guess_game_id = ObjectId()
            collection_mock = MagicMock()
            db_connection_mock.__getitem__.return_value = collection_mock
            collection_mock.find_one_and_delete.return_value = None

            # when & then
            with self.assertRaises(NotFoundException):
                model.delete(str(nonexistent_guess_game_id))

        tests = [
            deletes_and_confirms_deletion,
            fails_to_delete_a_guess_game_because_id_is_invalid,
            fails_to_delete_a_nonexistent_guess_game
        ]

        self.run_subtests(tests, after_each=db_connection_mock.reset_mock)
