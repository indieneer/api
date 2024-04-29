from unittest.mock import MagicMock


def mock_app_config(mock: MagicMock, config: dict):
    mock.__getitem__.side_effect = lambda key: config[key]

    return mock
