from app.models import ModelsExtension
from app.models.game_guesses import GameGuess, GameGuessCreate, GameGuessesModel
from app.services import Database
from bson import ObjectId
from typing import Union


class GameGuessesFactory:
    db: Database
    model: GameGuessesModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, game_guess_id: ObjectId):
        self.db.connection[self.models.game_guesses.collection].delete_one({
            "_id": game_guess_id})

    def create(self, input_data: Union[GameGuess, GameGuessCreate]):
        if isinstance(input_data, GameGuess):
            game_guess = self.models.game_guesses.put(input_data)
        else:
            game_guess = self.models.game_guesses.create(input_data=input_data)

        return game_guess, lambda: self.cleanup(game_guess._id)
