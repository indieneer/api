from typing import cast
from unittest.mock import MagicMock


def mock_collection(db: MagicMock, collection: str):
    collection_mock = db.connection[collection]

    # keep track of mocked collections, so that when mocking a wrong collection name we will know about this
    if isinstance(db.connection.mocked_collections, list) == False:
        db.connection._mocked_collections = []
        db.connection.__getitem__.side_effect = lambda c: collection_mock if c in db.connection._mocked_collections else None

    db.connection._mocked_collections.append(collection)

    return collection_mock


def mock_collection_method(db: MagicMock, collection: str, method: str):
    mock = mock_collection(db, collection)

    return cast(MagicMock, mock.__getattr__(method))


def mock_client_session(db: MagicMock):
    mock_session = MagicMock()
    db.client.start_session.return_value = mock_session

    return mock_session
