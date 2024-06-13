from bson import ObjectId
from pymongo import ReturnDocument
from dataclasses import dataclass
from typing import Optional, List, Union
from app.models.exceptions import NotFoundException
from app.models.base import Serializable, BaseDocument
from app.services import Database


class GuessGame(BaseDocument):
    product_id: Union[ObjectId, str]
    type: str
    data: dict

    def __init__(
            self,
            product_id: Union[ObjectId, str],
            type: str,
            data: dict,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.product_id = ObjectId(product_id)
        self.type = type
        self.data = data


@dataclass
class GuessGameCreate(Serializable):
    product_id: Union[ObjectId, str]
    type: str
    data: dict


@dataclass
class GuessGamePatch(Serializable):
    product_id: Optional[Union[ObjectId, str]] = None
    type: Optional[str] = None
    data: Optional[dict] = None


class GuessGamesModel:
    db: Database
    collection: str = "guess_games"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, guess_game_id: str) -> Optional[GuessGame]:
        """
        Retrieve a guess game by its ID.

        :param str guess_game_id: The unique identifier of the guess game to retrieve.
        :return: The GuessGame object if found, otherwise None.
        :rtype: Optional[GuessGame]
        """
        game_data = self.db.connection[self.collection].find_one({"_id": ObjectId(guess_game_id)})
        if game_data:
            return GuessGame(**game_data)
        return None

    def get_all(self) -> List[GuessGame]:
        """
        Retrieve all guess games from the database.

        :return: A list of GuessGame objects.
        :rtype: List[GuessGame]
        """
        guess_games = [GuessGame(**item) for item in self.db.connection[self.collection].find()]
        return guess_games if guess_games else []

    def create(self, input_data: GuessGameCreate) -> GuessGame:
        """
        Create a new guess game in the database.

        :param GuessGameCreate input_data: The data for creating a new guess game.
        :return: The created GuessGame object.
        :rtype: GuessGame
        """
        guess_game_data = input_data.to_bson()
        self.db.connection[self.collection].insert_one(guess_game_data)
        return GuessGame(**guess_game_data)

    def put(self, guess_game: GuessGame) -> GuessGame:
        """
        Update a guess game in the database.

        This method directly inserts a guess game (assumed pre-existing) into the database, effectively replacing any existing game with the same ID.
        It returns the GuessGame object initialized with the updated guess game's details.

        :param GuessGame guess_game: The guess game data to be updated.
        :return: The updated guess game data.
        :rtype: GuessGame
        """
        self.db.connection[self.collection].insert_one(guess_game.to_bson())
        return guess_game

    def patch(self, guess_game_id: str, input_data: GuessGamePatch) -> GuessGame:
        """
        Update a guess game in the database based on its game ID.

        This method updates the guess game specified by the guess_game_id using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str guess_game_id: The unique identifier of the guess game to be updated.
        :param GuessGamePatch input_data: The data to update the guess game with.
        :return: The updated GuessGame object, or raises NotFoundException if the guess game is not found.
        :rtype: GuessGame
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        updated_game = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(guess_game_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if not updated_game:
            raise NotFoundException(GuessGame.__name__)
        return GuessGame(**updated_game)

    def delete(self, game_id: str) -> GuessGame:
        """
        Delete a guess game from the database by its ID.

        :param str game_id: The unique identifier of the guess game to delete.
        :return: The deleted GuessGame object, or raises NotFoundException if the guess game is not found.
        :rtype: GuessGame
        """
        game_data = self.db.connection[self.collection].find_one_and_delete({'_id': ObjectId(game_id)})
        if game_data:
            return GuessGame(**game_data)
        raise NotFoundException("Guess Game not found")
