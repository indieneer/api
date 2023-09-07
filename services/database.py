from pymongo import MongoClient


class Database:
    TIMEOUT_TIME = 500

    client = MongoClient(
        timeoutMS=TIMEOUT_TIME,
        retryWrites=False,
        waitQueueTimeoutMS=TIMEOUT_TIME,
        serverSelectionTimeoutMS=TIMEOUT_TIME,
        connectTimeoutMS=TIMEOUT_TIME * 3,
    )
