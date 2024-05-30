from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.daily_guess_games import DailyGuessGamePatch, DailyGuessGameCreate
from lib.http_utils import respond_success, respond_error

daily_guess_games_controller = Blueprint('daily_guess_games', __name__, url_prefix='/daily_guess_games')


@daily_guess_games_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_daily_guess_games():
    """
    Retrieve all daily guess games.

    This endpoint returns a list of all daily guess games from the database.
    Requires authentication and admin privileges.
    """
    daily_guess_games_model = get_models(current_app).daily_guess_games
    daily_guess_games_list = daily_guess_games_model.get_all()
    return respond_success([daily_guess_game.to_json() for daily_guess_game in daily_guess_games_list])


@daily_guess_games_controller.route('/<string:daily_guess_game_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_daily_guess_game_by_id(daily_guess_game_id):
    """
    Retrieve a single daily guess game by ID.

    This endpoint returns the details of a specific daily guess game.
    Requires authentication and admin privileges.
    """
    daily_guess_games_model = get_models(current_app).daily_guess_games
    daily_guess_game = daily_guess_games_model.get(daily_guess_game_id)
    if daily_guess_game:
        return respond_success(daily_guess_game.to_json())
    else:
        return respond_error(f'Daily guess game with ID {daily_guess_game_id} not found', 404)


@daily_guess_games_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_daily_guess_game():
    """
    Create a new daily guess game.

    This endpoint creates a new daily guess game with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    daily_guess_games_model = get_models(current_app).daily_guess_games
    try:
        daily_guess_game_data = DailyGuessGameCreate(**data)
        new_daily_guess_game = daily_guess_games_model.create(daily_guess_game_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_daily_guess_game.to_json(), status_code=201)


@daily_guess_games_controller.route('/<string:daily_guess_game_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_daily_guess_game(daily_guess_game_id):
    """
    Update an existing daily guess game.

    This endpoint updates a daily guess game's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    daily_guess_game_patch_data = DailyGuessGamePatch(**data)
    daily_guess_games_model = get_models(current_app).daily_guess_games
    updated_daily_guess_game = daily_guess_games_model.patch(daily_guess_game_id, daily_guess_game_patch_data)

    if updated_daily_guess_game:
        return respond_success(updated_daily_guess_game.to_json())
    else:
        return respond_error(f'Daily guess game with ID {daily_guess_game_id} not found', 404)


@daily_guess_games_controller.route('/<string:daily_guess_game_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_daily_guess_game(daily_guess_game_id):
    """
    Delete a daily guess game by ID.

    This endpoint removes a daily guess game from the database.
    Requires authentication and admin privileges.
    """
    daily_guess_games_model = get_models(current_app).daily_guess_games
    deleted_daily_guess_game = daily_guess_games_model.delete(daily_guess_game_id)
    if deleted_daily_guess_game:
        return respond_success({'message': f'Daily guess game {daily_guess_game_id} successfully deleted'})
    else:
        return respond_error(f'Daily guess game with ID {daily_guess_game_id} not found', 404)

