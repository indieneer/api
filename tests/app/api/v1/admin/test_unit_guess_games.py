import datetime
from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.admin.guess_games import get_guess_game_by_id, create_guess_game, delete_guess_game, update_guess_game

from tests import UnitTest
from app.models.guess_games import GuessGameCreate, GuessGame, GuessGamePatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException


class GuessGamesTestCase(UnitTest):

    @patch("app.api.v1.admin.guess_games.get_models")
    def test_create_guess_game(self, get_models: MagicMock):
        endpoint = "/guess_games"
        self.app.route(endpoint, methods=["POST"])(create_guess_game)

        create_guess_game_mock = get_models.return_value.guess_games.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_guess_game():
            # given
            mock_guess_game = GuessGame(product_id=ObjectId(),
                                       type="attributes",
                                       data={"key": "value"}
                                       )
            create_guess_game_mock.return_value = mock_guess_game

            expected_input = GuessGameCreate(
                product_id=str(mock_guess_game.product_id),
                type=mock_guess_game.type,
                data=mock_guess_game.data
            )

            expected_response = {
                "status": "ok",
                "data": mock_guess_game.to_json()
            }

            # when
            response = call_api({
                "product_id": str(expected_input.product_id),
                "type": expected_input.type,
                "data": expected_input.data
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_guess_game_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_guess_game_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"data": "invalid"})

            # then
            create_guess_game_mock.assert_not_called()

        tests = [
            creates_and_returns_a_guess_game,
            fails_to_create_a_guess_game_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_guess_game_mock.reset_mock)

    @patch("app.api.v1.admin.guess_games.get_models")
    def test_get_guess_game_by_id(self, get_models: MagicMock):
        endpoint = "/admin/guess_games/<string:guess_game_id>"
        self.app.route(endpoint, methods=["GET"])(get_guess_game_by_id)

        get_guess_game_mock = get_models.return_value.guess_games.get

        def call_api(guess_game_id):
            return self.test_client.get(
                endpoint.replace("<string:guess_game_id>", guess_game_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_a_guess_game():
            # given
            mock_guess_game_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_guess_game = GuessGame(product_id=ObjectId(),
                                       type="attributes",
                                       data={"key": "specific_value"},
                                       _id=mock_guess_game_id)
            get_guess_game_mock.return_value = mock_guess_game

            expected_response = {
                "status": "ok",
                "data": mock_guess_game.to_json()
            }

            # when
            response = call_api(mock_guess_game_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_guess_game_mock.assert_called_once_with(mock_guess_game_id)

        def does_not_find_a_guess_game_and_returns_an_error():
            # given
            mock_id = "1"
            get_guess_game_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Guess game with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_guess_game_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_guess_game,
            does_not_find_a_guess_game_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_guess_game_mock.reset_mock)

    @patch("app.api.v1.admin.guess_games.get_models")
    def test_update_guess_game(self, get_models: MagicMock):
        endpoint = "/admin/guess_games/<string:guess_game_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_guess_game)

        update_guess_game_mock = get_models.return_value.guess_games.patch

        def call_api(guess_game_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:guess_game_id>", guess_game_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_guess_game():
            # given
            mock_guess_game_id = "507f1f77bcf86cd799439011"
            updated_fields = {"data": {"key": "updated_value"}}
            mock_guess_game = GuessGame(product_id=ObjectId(),
                                       type="attributes",
                                       data={"key": "value"},
                                )

            update_guess_game_mock.return_value = mock_guess_game

            expected_response = {
                "status": "ok",
                "data": mock_guess_game.to_json()
            }

            # when
            response = call_api(mock_guess_game_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_guess_game_mock.assert_called_once_with(mock_guess_game_id, GuessGamePatch(**updated_fields))

        tests = [
            updates_and_returns_the_guess_game,
        ]

        self.run_subtests(tests, after_each=update_guess_game_mock.reset_mock)

    @patch("app.api.v1.admin.guess_games.get_models")
    def test_delete_guess_game(self, get_models: MagicMock):
        endpoint = "/admin/guess_games/<string:guess_game_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_guess_game)

        delete_guess_game_mock = get_models.return_value.guess_games.delete

        def call_api(guess_game_id):
            return self.test_client.delete(
                endpoint.replace("<string:guess_game_id>", guess_game_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_guess_game():
            # given
            mock_guess_game_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Guess game {mock_guess_game_id} successfully deleted"
            }

            # when
            response = call_api(mock_guess_game_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_guess_game_mock.assert_called_once_with(mock_guess_game_id)

        def fails_to_delete_a_nonexistent_guess_game():
            # given
            mock_id = "2"
            delete_guess_game_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Guess game with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_guess_game_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_guess_game,
            fails_to_delete_a_nonexistent_guess_game
        ]

        self.run_subtests(tests, after_each=delete_guess_game_mock.reset_mock)
