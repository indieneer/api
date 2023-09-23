from pymongo import MongoClient, database


class Database:
    __client: MongoClient
    __connection: database.Database

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

        self.__connection = self.__client.get_default_database()

    @property
    def client(self):
        return self.__client

    @property
    def connection(self):
        return self.__connection
