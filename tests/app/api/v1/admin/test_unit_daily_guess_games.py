import datetime
from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.admin.daily_guess_games import get_daily_guess_game_by_id, create_daily_guess_game, delete_daily_guess_game, update_daily_guess_game

from tests import UnitTest
from app.models.daily_guess_games import DailyGuessGameCreate, DailyGuessGame, DailyGuessGamePatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException


class DailyGuessGamesTestCase(UnitTest):

    @patch("app.api.v1.admin.daily_guess_games.get_models")
    def test_create_daily_guess_game(self, get_models: MagicMock):
        endpoint = "/daily_guess_games"
        self.app.route(endpoint, methods=["POST"])(create_daily_guess_game)

        create_daily_guess_game_mock = get_models.return_value.daily_guess_games.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_daily_guess_game():
            # given
            mock_daily_guess_game = DailyGuessGame(product_id=ObjectId(),
                                                   type="attributes",
                                                   data={"key": "value"},
                                                   display_at="2036-02-03T00:00:00"
                                                   )
            create_daily_guess_game_mock.return_value = mock_daily_guess_game

            expected_input = DailyGuessGameCreate(
                product_id=str(mock_daily_guess_game.product_id),
                type=mock_daily_guess_game.type,
                data=mock_daily_guess_game.data,
                display_at=str(mock_daily_guess_game.display_at)
            )

            expected_response = {
                "status": "ok",
                "data": mock_daily_guess_game.to_json()
            }

            # when
            response = call_api({
                "product_id": str(expected_input.product_id),
                "type": expected_input.type,
                "data": expected_input.data,
                "display_at": "2036-02-03 00:00:00"
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_daily_guess_game_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_daily_guess_game_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"data": "invalid"})

            # then
            create_daily_guess_game_mock.assert_not_called()

        tests = [
            creates_and_returns_a_daily_guess_game,
            fails_to_create_a_daily_guess_game_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_daily_guess_game_mock.reset_mock)

    @patch("app.api.v1.admin.daily_guess_games.get_models")
    def test_get_daily_guess_game_by_id(self, get_models: MagicMock):
        endpoint = "/admin/daily_guess_games/<string:daily_guess_game_id>"
        self.app.route(endpoint, methods=["GET"])(get_daily_guess_game_by_id)

        get_daily_guess_game_mock = get_models.return_value.daily_guess_games.get

        def call_api(daily_guess_game_id):
            return self.test_client.get(
                endpoint.replace("<string:daily_guess_game_id>", daily_guess_game_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_a_daily_guess_game():
            # given
            mock_daily_guess_game_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_daily_guess_game = DailyGuessGame(product_id=ObjectId(),
                                                   type="attributes",
                                                   data={"key": "specific_value"},
                                                   display_at="2036-02-03T00:00:00",
                                                   _id=mock_daily_guess_game_id)
            get_daily_guess_game_mock.return_value = mock_daily_guess_game

            expected_response = {
                "status": "ok",
                "data": mock_daily_guess_game.to_json()
            }

            # when
            response = call_api(mock_daily_guess_game_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_daily_guess_game_mock.assert_called_once_with(mock_daily_guess_game_id)

        def does_not_find_a_daily_guess_game_and_returns_an_error():
            # given
            mock_id = "1"
            get_daily_guess_game_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Daily guess game with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_daily_guess_game_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_daily_guess_game,
            does_not_find_a_daily_guess_game_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_daily_guess_game_mock.reset_mock)

    @patch("app.api.v1.admin.daily_guess_games.get_models")
    def test_update_daily_guess_game(self, get_models: MagicMock):
        endpoint = "/admin/daily_guess_games/<string:daily_guess_game_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_daily_guess_game)

        update_daily_guess_game_mock = get_models.return_value.daily_guess_games.patch

        def call_api(daily_guess_game_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:daily_guess_game_id>", daily_guess_game_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_daily_guess_game():
            # given
            mock_daily_guess_game_id = "507f1f77bcf86cd799439011"
            updated_fields = {"data": {"key": "updated_value"}}
            mock_daily_guess_game = DailyGuessGame(product_id=ObjectId(),
                                                   type="attributes",
                                                   data={"key": "value"},
                                                   display_at="2036-02-03T00:00:00"
                                            )

            update_daily_guess_game_mock.return_value = mock_daily_guess_game

            expected_response = {
                "status": "ok",
                "data": mock_daily_guess_game.to_json()
            }

            # when
            response = call_api(mock_daily_guess_game_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_daily_guess_game_mock.assert_called_once_with(mock_daily_guess_game_id, DailyGuessGamePatch(**updated_fields))

        tests = [
            updates_and_returns_the_daily_guess_game,
        ]

        self.run_subtests(tests, after_each=update_daily_guess_game_mock.reset_mock)

    @patch("app.api.v1.admin.daily_guess_games.get_models")
    def test_delete_daily_guess_game(self, get_models: MagicMock):
        endpoint = "/admin/daily_guess_games/<string:daily_guess_game_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_daily_guess_game)

        delete_daily_guess_game_mock = get_models.return_value.daily_guess_games.delete

        def call_api(daily_guess_game_id):
            return self.test_client.delete(
                endpoint.replace("<string:daily_guess_game_id>", daily_guess_game_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_daily_guess_game():
            # given
            mock_daily_guess_game_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Daily guess game {mock_daily_guess_game_id} successfully deleted"
            }

            # when
            response = call_api(mock_daily_guess_game_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_daily_guess_game_mock.assert_called_once_with(mock_daily_guess_game_id)

        def fails_to_delete_a_nonexistent_daily_guess_game():
            # given
            mock_id = "2"
            delete_daily_guess_game_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Daily guess game with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_daily_guess_game_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_daily_guess_game,
            fails_to_delete_a_nonexistent_daily_guess_game
        ]

        self.run_subtests(tests, after_each=delete_daily_guess_game_mock.reset_mock)

