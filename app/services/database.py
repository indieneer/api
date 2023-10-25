from pymongo import MongoClient


class Database:
    """
    Used to interact with the database
    """

    __client: MongoClient

    def __init__(
        self,
        uri: str,
        timeoutMS: int = 500
    ) -> None:
        self.__client = MongoClient(
            uri,
            timeoutMS=timeoutMS,
            retryWrites=False,
            waitQueueTimeoutMS=timeoutMS,
            serverSelectionTimeoutMS=timeoutMS,
            connectTimeoutMS=timeoutMS * 3,
        )

    @property
    def client(self):
        return self.__client

    @property
    def connection(self):
        return self.__client.get_default_database()
