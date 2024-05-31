from bson import ObjectId
from pymongo import ReturnDocument
from dataclasses import dataclass
from typing import Optional, List, Union
from app.models.exceptions import NotFoundException
from app.models.base import Serializable, BaseDocument
from app.services import Database
from datetime import datetime


class GameGuess(BaseDocument):
    daily_guess_game_id: Union[ObjectId, str]
    ip: str
    profile_id: Optional[Union[ObjectId, str]] = None
    attempts: List[dict]
    guessed_at: Optional[Union[datetime, str]] = None

    def __init__(
            self,
            daily_guess_game_id: Union[ObjectId, str],
            ip: str,
            attempts: List[dict],
            guessed_at: Optional[Union[datetime, str]] = None,
            profile_id: Optional[Union[ObjectId, str]] = None,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.daily_guess_game_id = ObjectId(daily_guess_game_id)
        self.ip = ip
        self.profile_id = ObjectId(profile_id) if profile_id else None
        self.attempts = attempts
        self.guessed_at = guessed_at if isinstance(guessed_at, datetime) else \
                          datetime.fromisoformat(guessed_at) if isinstance(guessed_at, str) else \
                          None  # TODO: Better indent


@dataclass
class GameGuessCreate(Serializable):
    daily_guess_game_id: Union[ObjectId, str]
    ip: str
    attempts: List[dict]
    profile_id: Optional[Union[ObjectId, str]] = None
    guessed_at: Optional[Union[datetime, str]] = None


@dataclass
class GameGuessPatch(Serializable):
    daily_guess_game_id: Optional[Union[ObjectId, str]] = None
    ip: Optional[str] = None
    attempts: Optional[List[dict]] = None
    guessed_at: Optional[datetime] = None
    profile_id: Optional[Union[ObjectId, str]] = None


class GameGuessesModel:
    db: Database
    collection: str = "game_guesses"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, game_guess_id: str) -> Optional[GameGuess]:
        """
        Retrieve a game guess by its ID.

        :param str game_guess_id: The unique identifier of the game guess to retrieve.
        :return: The GameGuess object if found, otherwise None.
        :rtype: Optional[GameGuess]
        """
        guess_data = self.db.connection[self.collection].find_one({"_id": ObjectId(game_guess_id)})
        if guess_data:
            return GameGuess(**guess_data)
        return None

    def get_all(self) -> List[GameGuess]:
        """
        Retrieve all game guesses from the database.

        :return: A list of GameGuess objects.
        :rtype: List[GameGuess]
        """
        game_guesses = [GameGuess(**item) for item in self.db.connection[self.collection].find()]
        return game_guesses if game_guesses else []

    def create(self, input_data: GameGuessCreate) -> GameGuess:
        """
        Create a new game guess in the database.

        :param GameGuessCreate input_data: The data for creating a new game guess.
        :return: The created GameGuess object.
        :rtype: GameGuess
        """
        game_guess_data = input_data.to_bson()
        self.db.connection[self.collection].insert_one(game_guess_data)
        return GameGuess(**game_guess_data)

    def put(self, game_guess: GameGuess) -> GameGuess:
        """
        Update a game guess in the database.

        This method directly inserts a game guess (assumed pre-existing) into the database, effectively replacing any existing game with the same ID.
        It returns the GameGuess object initialized with the updated game guess's details.

        :param GameGuess game_guess: The game guess data to be updated.
        :return: The updated game guess data.
        :rtype: GameGuess
        """
        self.db.connection[self.collection].insert_one(game_guess.to_bson())
        return game_guess

    def patch(self, game_guess_id: str, input_data: GameGuessPatch) -> GameGuess:
        """
        Update a game guess in the database based on its game ID.

        This method updates the game guess specified by the game_guess_id using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str game_guess_id: The unique identifier of the game guess to be updated.
        :param GameGuessPatch input_data: The data to update the game guess with.
        :return: The updated GameGuess object, or raises NotFoundException if the game guess is not found.
        :rtype: GameGuess
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        updated_game = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(game_guess_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if not updated_game:
            raise NotFoundException(GameGuess.__name__)
        return GameGuess(**updated_game)

    def delete(self, game_guess_id: str) -> GameGuess:
        """
        Delete a game guess from the database by its ID.

        :param str game_guess_id: The unique identifier of the game guess to delete.
        :return: The deleted GameGuess object, or raises NotFoundException if the game guess is not found.
        :rtype: GameGuess
        """
        guess_data = self.db.connection[self.collection].find_one_and_delete({'_id': ObjectId(game_guess_id)})
        if guess_data:
            return GameGuess(**guess_data)
        raise NotFoundException("Game Guess not found")

