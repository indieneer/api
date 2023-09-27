from unittest.mock import Mock, MagicMock, patch


def mock_database_connection(get_services: MagicMock):
    return get_services.return_value.db.connection
