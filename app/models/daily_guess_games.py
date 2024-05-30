from bson import ObjectId
from pymongo import ReturnDocument
from dataclasses import dataclass
from typing import Optional, List, Union
from app.models.exceptions import NotFoundException
from app.models.base import Serializable, BaseDocument
from app.services import Database
from datetime import datetime


class DailyGuessGame(BaseDocument):
    guess_game_id: Optional[Union[ObjectId, str]] = None
    product_id: Union[ObjectId, str]
    type: str
    data: dict
    display_at: Union[datetime, str]

    def __init__(
            self,
            product_id: Union[ObjectId, str],
            type: str,
            data: dict,
            display_at: Union[datetime, str],
            guess_game_id: Optional[Union[ObjectId, str]] = None,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.guess_game_id = ObjectId(guess_game_id) if guess_game_id else None
        self.product_id = ObjectId(product_id)
        self.type = type
        self.data = data
        self.display_at = display_at if isinstance(display_at, datetime) else datetime.fromisoformat(display_at)


@dataclass
class DailyGuessGameCreate(Serializable):
    type: str
    data: dict
    display_at: Union[datetime, str]
    product_id: Optional[Union[ObjectId, str]] = None
    guess_game_id: Optional[Union[ObjectId, str]] = None


@dataclass
class DailyGuessGamePatch(Serializable):
    product_id: Optional[Union[ObjectId, str]] = None
    type: Optional[str] = None
    data: Optional[dict] = None
    display_at: Optional[Union[datetime, str]] = None
    guess_game_id: Optional[Union[ObjectId, str]] = None


class DailyGuessGamesModel:
    db: Database
    collection: str = "daily_guess_games"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, daily_guess_game_id: str) -> Optional[DailyGuessGame]:
        """
        Retrieve a daily guess game by its ID.

        :param str daily_guess_game_id: The unique identifier of the daily guess game to retrieve.
        :return: The DailyGuessGame object if found, otherwise None.
        :rtype: Optional[DailyGuessGame]
        """
        game_data = self.db.connection[self.collection].find_one({"_id": ObjectId(daily_guess_game_id)})
        if game_data:
            return DailyGuessGame(**game_data)
        return None

    def get_all(self) -> List[DailyGuessGame]:
        """
        Retrieve all daily guess games from the database.

        :return: A list of DailyGuessGame objects.
        :rtype: List[DailyGuessGame]
        """
        daily_guess_games = [DailyGuessGame(**item) for item in self.db.connection[self.collection].find()]
        return daily_guess_games if daily_guess_games else []

    def create(self, input_data: DailyGuessGameCreate) -> DailyGuessGame:
        """
        Create a new daily guess game in the database.

        :param DailyGuessGameCreate input_data: The data for creating a new daily guess game.
        :return: The created DailyGuessGame object.
        :rtype: DailyGuessGame
        """
        daily_guess_game_data = input_data.to_bson()
        self.db.connection[self.collection].insert_one(daily_guess_game_data)
        return DailyGuessGame(**daily_guess_game_data)

    def put(self, daily_guess_game: DailyGuessGame) -> DailyGuessGame:
        """
        Update a daily guess game in the database.

        This method directly inserts a daily guess game (assumed pre-existing) into the database, effectively replacing any existing game with the same ID.
        It returns the DailyGuessGame object initialized with the updated daily guess game's details.

        :param DailyGuessGame daily_guess_game: The daily guess game data to be updated.
        :return: The updated daily guess game data.
        :rtype: DailyGuessGame
        """
        self.db.connection[self.collection].insert_one(daily_guess_game.to_bson())
        return daily_guess_game

    def patch(self, daily_guess_game_id: str, input_data: DailyGuessGamePatch) -> DailyGuessGame:
        """
        Update a daily guess game in the database based on its game ID.

        This method updates the daily guess game specified by the daily_guess_game_id using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str daily_guess_game_id: The unique identifier of the daily guess game to be updated.
        :param DailyGuessGamePatch input_data: The data to update the daily guess game with.
        :return: The updated DailyGuessGame object, or raises NotFoundException if the daily guess game is not found.
        :rtype: DailyGuessGame
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        updated_game = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(daily_guess_game_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if not updated_game:
            raise NotFoundException(DailyGuessGame.__name__)
        return DailyGuessGame(**updated_game)

    def delete(self, daily_guess_game_id: str) -> DailyGuessGame:
        """
        Delete a daily guess game from the database by its ID.

        :param str daily_guess_game_id: The unique identifier of the daily guess game to delete.
        :return: The deleted DailyGuessGame object, or raises NotFoundException if the daily guess game is not found.
        :rtype: DailyGuessGame
        """
        game_data = self.db.connection[self.collection].find_one_and_delete({'_id': ObjectId(daily_guess_game_id)})
        if game_data:
            return DailyGuessGame(**game_data)
        raise NotFoundException("Daily Guess Game not found")

