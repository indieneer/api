import datetime
from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.admin.game_guesses import get_game_guess_by_id, create_game_guess, delete_game_guess, update_game_guess

from tests import UnitTest
from app.models.game_guesses import GameGuessCreate, GameGuess, GameGuessPatch
from tests.utils.jwt import create_test_token
from app.api.exceptions import UnprocessableEntityException


class GameGuessesTestCase(UnitTest):

    @patch("app.api.v1.admin.game_guesses.get_models")
    def test_create_game_guess(self, get_models: MagicMock):
        endpoint = "/game_guesses"
        self.app.route(endpoint, methods=["POST"])(create_game_guess)

        create_game_guess_mock = get_models.return_value.game_guesses.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json',
                headers={"Authorization": "Bearer " +
                         create_test_token("", roles=["admin"])}
            )

        def creates_and_returns_a_game_guess():
            # given
            mock_game_guess = GameGuess(daily_guess_game_id=ObjectId(),
                                       ip="127.0.0.1",
                                       attempts=[{"product_id": "1234", "data": {"key": "value"}}]
                                       )
            create_game_guess_mock.return_value = mock_game_guess

            expected_input = GameGuessCreate(
                daily_guess_game_id=str(mock_game_guess.daily_guess_game_id),
                ip=mock_game_guess.ip,
                attempts=mock_game_guess.attempts,
                profile_id=mock_game_guess.profile_id,
                guessed_at=mock_game_guess.guessed_at
            )

            expected_response = {
                "status": "ok",
                "data": mock_game_guess.to_json()
            }

            # when
            response = call_api({
                "daily_guess_game_id": str(expected_input.daily_guess_game_id),
                "ip": expected_input.ip,
                "attempts": expected_input.attempts
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_game_guess_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_game_guess_when_body_is_invalid():
            # when
            with self.assertRaises(UnprocessableEntityException):
                call_api({"data": "invalid"})

            # then
            create_game_guess_mock.assert_not_called()

        tests = [
            creates_and_returns_a_game_guess,
            fails_to_create_a_game_guess_when_body_is_invalid
        ]

        self.run_subtests(tests, after_each=create_game_guess_mock.reset_mock)

    @patch("app.api.v1.admin.game_guesses.get_models")
    def test_get_game_guess_by_id(self, get_models: MagicMock):
        endpoint = "/admin/game_guesses/<string:game_guess_id>"
        self.app.route(endpoint, methods=["GET"])(get_game_guess_by_id)

        get_game_guess_mock = get_models.return_value.game_guesses.get

        def call_api(game_guess_id):
            return self.test_client.get(
                endpoint.replace("<string:game_guess_id>", game_guess_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def finds_and_returns_a_game_guess():
            # given
            mock_game_guess_id = "507f1f77bcf86cd799439011"  # Example ObjectId
            mock_game_guess = GameGuess(daily_guess_game_id=ObjectId(),
                                       ip="127.0.0.1",
                                       attempts=[{"product_id": "1234", "data": {"key": "specific_value"}}],
                                       _id=mock_game_guess_id)
            get_game_guess_mock.return_value = mock_game_guess

            expected_response = {
                "status": "ok",
                "data": mock_game_guess.to_json()
            }

            # when
            response = call_api(mock_game_guess_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_game_guess_mock.assert_called_once_with(mock_game_guess_id)

        def does_not_find_a_game_guess_and_returns_an_error():
            # given
            mock_id = "1"
            get_game_guess_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f'Game guess with ID {mock_id} not found'
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_game_guess_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_game_guess,
            does_not_find_a_game_guess_and_returns_an_error
        ]

        self.run_subtests(tests, after_each=get_game_guess_mock.reset_mock)

    @patch("app.api.v1.admin.game_guesses.get_models")
    def test_update_game_guess(self, get_models: MagicMock):
        endpoint = "/admin/game_guesses/<string:game_guess_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_game_guess)

        update_game_guess_mock = get_models.return_value.game_guesses.patch

        def call_api(game_guess_id, body):
            return self.test_client.patch(
                endpoint.replace("<string:game_guess_id>", game_guess_id),
                data=json.dumps(body),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def updates_and_returns_the_game_guess():
            # given
            mock_game_guess_id = "507f1f77bcf86cd799439011"
            updated_fields = {"attempts": [{"product_id": "1234", "data": {"key": "updated_value"}}]}
            mock_game_guess = GameGuess(daily_guess_game_id=ObjectId(),
                                       ip="127.0.0.1",
                                       attempts=[{"product_id": "1234", "data": {"key": "value"}}]
                                )

            update_game_guess_mock.return_value = mock_game_guess

            expected_response = {
                "status": "ok",
                "data": mock_game_guess.to_json()
            }

            # when
            response = call_api(mock_game_guess_id, updated_fields)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            update_game_guess_mock.assert_called_once_with(mock_game_guess_id, GameGuessPatch(**updated_fields))

        tests = [
            updates_and_returns_the_game_guess,
        ]

        self.run_subtests(tests, after_each=update_game_guess_mock.reset_mock)

    @patch("app.api.v1.admin.game_guesses.get_models")
    def test_delete_game_guess(self, get_models: MagicMock):
        endpoint = "/admin/game_guesses/<string:game_guess_id>"
        self.app.route(endpoint, methods=["DELETE"])(delete_game_guess)

        delete_game_guess_mock = get_models.return_value.game_guesses.delete

        def call_api(game_guess_id):
            return self.test_client.delete(
                endpoint.replace("<string:game_guess_id>", game_guess_id),
                headers={"Authorization": "Bearer " + create_test_token("", roles=["admin"])},
                content_type='application/json'
            )

        def deletes_the_game_guess():
            # given
            mock_game_guess_id = "507f1f77bcf86cd799439011"

            expected_response = {
                "message": f"Game guess {mock_game_guess_id} successfully deleted"
            }

            # when
            response = call_api(mock_game_guess_id)

            # then
            self.assertEqual(response.get_json()["data"], expected_response)
            self.assertEqual(response.status_code, 200)
            delete_game_guess_mock.assert_called_once_with(mock_game_guess_id)

        def fails_to_delete_a_nonexistent_game_guess():
            # given
            mock_id = "2"
            delete_game_guess_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": f"Game guess with ID {mock_id} not found"
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_game_guess_mock.assert_called_once_with(mock_id)

        tests = [
            deletes_the_game_guess,
            fails_to_delete_a_nonexistent_game_guess
        ]

        self.run_subtests(tests, after_each=delete_game_guess_mock.reset_mock)

