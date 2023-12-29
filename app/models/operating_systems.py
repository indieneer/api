from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from app.models.base import BaseDocument, Serializable

from .exceptions import NotFoundException


class OperatingSystem(BaseDocument):
    name: str

    def __init__(
        self,
        name: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.name = name


@dataclass
class OperatingSystemCreate(Serializable):
    name: str


@dataclass
class OperatingSystemPatch(Serializable):
    name: Optional[str] = None


class OperatingSystemsModel:
    db: Database
    collection: str = "operating_systems"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, operating_system_id: str):
        """
        Retrieve an operating system by its ID.

        This method searches for an operating system in the database using the provided ID.
        If found, it returns the operating system object.

        :param str operating_system_id: The unique identifier of the operating system.
        :return: An OperatingSystem object if found, otherwise None.
        :rtype: OperatingSystem or None
        """
        operating_system = self.db.connection[self.collection].find_one({"_id": ObjectId(operating_system_id)})

        if operating_system is not None:
            return OperatingSystem(**operating_system)

    def get_all(self):
        """
        Retrieve all operating systems.

        This method fetches all operating systems from the database.
        If operating systems are found, it returns a list of OperatingSystem objects; otherwise, an empty list.

        :return: A list of OperatingSystem objects or an empty list if no operating systems are found.
        :rtype: list
        """
        operating_systems = [OperatingSystem(**item) for item in self.db.connection[self.collection].find()]

        return operating_systems

    def create(self, input_data: OperatingSystemCreate):
        """
        Create a new operating system entry.

        This method takes the input data, converts it to a JSON format suitable for database insertion,
        and creates a new operating system in the database.

        :param OperatingSystemCreate input_data: The data required to create a new operating system.
        :return: The newly created OperatingSystem object.
        :rtype: OperatingSystem
        """
        # Prepare operating_system data for database insertion
        operating_system_data = OperatingSystem(**input_data.to_json()).to_bson()

        # Insert the new operating_system into the database
        self.db.connection[self.collection].insert_one(operating_system_data)

        return OperatingSystem(**operating_system_data)

    def put(self, input_data: OperatingSystem):
        """
        Create a new operating system or replace an existing one.

        This method takes an OperatingSystem object, removes its ID if it exists,
        and inserts it into the database, effectively creating a new operating system.

        :param OperatingSystem input_data: The operating system data for creation or replacement.
        :return: The newly created or replaced OperatingSystem object.
        :rtype: OperatingSystem
        """
        operating_system_data = input_data.to_bson()

        # Insert the new operating system into the database
        inserted_id = self.db.connection[self.collection].insert_one(operating_system_data).inserted_id
        operating_system_data["_id"] = inserted_id

        return OperatingSystem(**operating_system_data)

    def patch(self, operating_system_id: str, input_data: OperatingSystemPatch):
        """
        Update an existing operating system.

        This method updates fields of an existing operating system based on the provided ID and input data.
        It raises a ValueError if no valid fields are provided, and a NotFoundException if the operating system is not found.

        :param str operating_system_id: The ID of the operating system to update.
        :param OperatingSystemPatch input_data: The data containing updates for the operating system.
        :raises ValueError: If no valid fields are provided for update.
        :raises NotFoundException: If no operating system is found with the given ID.
        :return: The updated OperatingSystem object.
        :rtype: OperatingSystem
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_operating_system = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(operating_system_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_operating_system is not None:
            return OperatingSystem(**updated_operating_system)
        else:
            raise NotFoundException(OperatingSystem.__name__)

    def delete(self, operating_system_id: str):
        """
        Delete an operating system by its ID.

        This method removes an operating system from the database based on the provided ID.
        If the operation is successful, it returns the deleted operating system object.

        :param str operating_system_id: The unique identifier of the operating system to delete.
        :return: The deleted OperatingSystem object if the operation is successful, otherwise None.
        :rtype: OperatingSystem or None
        """
        operating_system = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(operating_system_id)}
        )

        if operating_system is not None:
            return OperatingSystem(**operating_system)
