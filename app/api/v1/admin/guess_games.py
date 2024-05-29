from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.guess_games import GuessGamePatch, GuessGameCreate
from lib.http_utils import respond_success, respond_error

guess_games_controller = Blueprint('guess_games', __name__, url_prefix='/guess_games')


@guess_games_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_guess_games():
    """
    Retrieve all guess games.

    This endpoint returns a list of all guess games from the database.
    Requires authentication and admin privileges.
    """
    guess_games_model = get_models(current_app).guess_games
    guess_games_list = guess_games_model.get_all()
    return respond_success([guess_game.to_json() for guess_game in guess_games_list])


@guess_games_controller.route('/<string:guess_game_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_guess_game_by_id(guess_game_id):
    """
    Retrieve a single guess game by ID.

    This endpoint returns the details of a specific guess game.
    Requires authentication and admin privileges.
    """
    guess_games_model = get_models(current_app).guess_games
    guess_game = guess_games_model.get(guess_game_id)
    if guess_game:
        return respond_success(guess_game.to_json())
    else:
        return respond_error(f'Guess game with ID {guess_game_id} not found', 404)


@guess_games_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_guess_game():
    """
    Create a new guess game.

    This endpoint creates a new guess game with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    guess_games_model = get_models(current_app).guess_games
    try:
        guess_game_data = GuessGameCreate(**data)
        new_guess_game = guess_games_model.create(guess_game_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_guess_game.to_json(), status_code=201)


@guess_games_controller.route('/<string:guess_game_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_guess_game(guess_game_id):
    """
    Update an existing guess game.

    This endpoint updates a guess game's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    guess_game_patch_data = GuessGamePatch(**data)
    guess_games_model = get_models(current_app).guess_games
    updated_guess_game = guess_games_model.patch(guess_game_id, guess_game_patch_data)

    if updated_guess_game:
        return respond_success(updated_guess_game.to_json())
    else:
        return respond_error(f'Guess game with ID {guess_game_id} not found', 404)


@guess_games_controller.route('/<string:guess_game_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_guess_game(guess_game_id):
    """
    Delete a guess game by ID.

    This endpoint removes a guess game from the database.
    Requires authentication and admin privileges.
    """
    guess_games_model = get_models(current_app).guess_games
    deleted_guess_game = guess_games_model.delete(guess_game_id)
    if deleted_guess_game:
        return respond_success({'message': f'Guess game {guess_game_id} successfully deleted'})
    else:
        return respond_error(f'Guess game with ID {guess_game_id} not found', 404)
