from pymongo import MongoClient
from os import environ as env

class Database:
    TIMEOUT_TIME = 500

    client = MongoClient(
        env.get("MONGO_URI"),
        timeoutMS=TIMEOUT_TIME,
        retryWrites=False,
        waitQueueTimeoutMS=TIMEOUT_TIME,
        serverSelectionTimeoutMS=TIMEOUT_TIME,
        connectTimeoutMS=TIMEOUT_TIME * 3,
    )
