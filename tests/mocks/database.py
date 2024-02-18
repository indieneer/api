from typing import cast
from unittest.mock import MagicMock


def mock_collection(db: MagicMock, collection: str):
    collection_mock = MagicMock()
    db.connection.__getitem__.side_effect = lambda c: collection_mock if c == collection else None

    return collection_mock


def mock_collection_method(db: MagicMock, collection: str, method: str):
    mock = mock_collection(db, collection)

    return cast(MagicMock, mock.__getattr__(method))


def mock_client_session(db: MagicMock):
    mock_session = MagicMock()
    db.client.start_session.return_value = mock_session

    return mock_session
