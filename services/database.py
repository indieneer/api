from pymongo import MongoClient
from config import configuration


class Database:
    TIMEOUT_TIME = 500

    client = None

    @staticmethod
    def initialize():
        Database.client = MongoClient(
            configuration["MONGO_URI"],
            timeoutMS=Database.TIMEOUT_TIME,
            retryWrites=False,
            waitQueueTimeoutMS=Database.TIMEOUT_TIME,
            serverSelectionTimeoutMS=Database.TIMEOUT_TIME,
            connectTimeoutMS=Database.TIMEOUT_TIME * 3,
        )
