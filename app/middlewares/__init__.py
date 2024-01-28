from typing import Dict
from flask import request


# Error handler
# Format error response and append status code
class AuthError(Exception):
    def __init__(self, error: Dict, status_code: int):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", "")
    parts = auth.split()

    if len(parts) == 0:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with"
                             " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

    token = parts[1]
    return token


from .requires_auth import requires_auth  # nopep8
from .requires_role import requires_role  # nopep8
from .requires_service_account import requires_service_account  # nopep8
