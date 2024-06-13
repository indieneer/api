from app.models import ModelsExtension
from app.models.guess_games import GuessGame, GuessGameCreate, GuessGamesModel
from app.services import Database
from bson import ObjectId
from typing import Union


class GuessGamesFactory:
    db: Database
    model: GuessGamesModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, guess_game_id: ObjectId):
        self.db.connection[self.models.guess_games.collection].delete_one({
            "_id": guess_game_id})

    def create(self, input_data: Union[GuessGame, GuessGameCreate]):
        if isinstance(input_data, GuessGame):
            guess_game = self.models.guess_games.put(input_data)
        else:
            guess_game = self.models.guess_games.create(input_data=input_data)

        return guess_game, lambda: self.cleanup(guess_game._id)
