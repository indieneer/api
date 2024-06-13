from app.models import ModelsExtension
from app.models.daily_guess_games import DailyGuessGame, DailyGuessGameCreate, DailyGuessGamesModel
from app.services import Database
from bson import ObjectId
from typing import Union


class DailyGuessGamesFactory:
    db: Database
    model: DailyGuessGamesModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, daily_guess_game_id: ObjectId):
        self.db.connection[self.models.daily_guess_games.collection].delete_one({
            "_id": daily_guess_game_id})

    def create(self, input_data: Union[DailyGuessGame, DailyGuessGameCreate]):
        if isinstance(input_data, DailyGuessGame):
            daily_guess_game = self.models.daily_guess_games.put(input_data)
        else:
            daily_guess_game = self.models.daily_guess_games.create(input_data=input_data)

        return daily_guess_game, lambda: self.cleanup(daily_guess_game._id)
