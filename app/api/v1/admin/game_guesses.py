from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.game_guesses import GameGuessPatch, GameGuessCreate
from lib.http_utils import respond_success, respond_error

game_guesses_controller = Blueprint('game_guesses', __name__, url_prefix='/game_guesses')


@game_guesses_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_game_guesses():
    """
    Retrieve all game guesses.

    This endpoint returns a list of all game guesses from the database.
    Requires authentication and admin privileges.
    """
    game_guesses_model = get_models(current_app).game_guesses
    game_guesses_list = game_guesses_model.get_all()
    return respond_success([game_guess.to_json() for game_guess in game_guesses_list])


@game_guesses_controller.route('/<string:game_guess_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_game_guess_by_id(game_guess_id):
    """
    Retrieve a single game guess by ID.

    This endpoint returns the details of a specific game guess.
    Requires authentication and admin privileges.
    """
    game_guesses_model = get_models(current_app).game_guesses
    game_guess = game_guesses_model.get(game_guess_id)
    if game_guess:
        return respond_success(game_guess.to_json())
    else:
        return respond_error(f'Game guess with ID {game_guess_id} not found', 404)


@game_guesses_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_game_guess():
    """
    Create a new game guess.

    This endpoint creates a new game guess with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    game_guesses_model = get_models(current_app).game_guesses
    try:
        game_guess_data = GameGuessCreate(**data)
        new_game_guess = game_guesses_model.create(game_guess_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_game_guess.to_json(), status_code=201)


@game_guesses_controller.route('/<string:game_guess_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_game_guess(game_guess_id):
    """
    Update an existing game guess.

    This endpoint updates a game guess's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    game_guess_patch_data = GameGuessPatch(**data)
    game_guesses_model = get_models(current_app).game_guesses
    updated_game_guess = game_guesses_model.patch(game_guess_id, game_guess_patch_data)

    if updated_game_guess:
        return respond_success(updated_game_guess.to_json())
    else:
        return respond_error(f'Game guess with ID {game_guess_id} not found', 404)


@game_guesses_controller.route('/<string:game_guess_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_game_guess(game_guess_id):
    """
    Delete a game guess by ID.

    This endpoint removes a game guess from the database.
    Requires authentication and admin privileges.
    """
    game_guesses_model = get_models(current_app).game_guesses
    deleted_game_guess = game_guesses_model.delete(game_guess_id)
    if deleted_game_guess:
        return respond_success({'message': f'Game guess {game_guess_id} successfully deleted'})
    else:
        return respond_error(f'Game guess with ID {game_guess_id} not found', 404)
