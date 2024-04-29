from typing import cast
from unittest.mock import MagicMock


def mock_auth_method(firebase: MagicMock, method: str):
    auth_mock = firebase.auth

    return cast(MagicMock, auth_mock.__getattr__(method))
