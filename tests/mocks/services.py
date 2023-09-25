from unittest.mock import Mock, MagicMock, patch


def mock_database_connection(get_services: MagicMock):
    connection = Mock()

    get_services.return_value.db.connection = connection

    return connection
