from functools import wraps
from typing import cast

from flask import Flask, g, current_app

from app.services import get_services
from . import AuthError, get_token_auth_header


class RequiresAuthExtension:
    """Workaround to inject custom JWT validator for unit testing
    """

    KEY = "requires_auth"

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self

    def verify_token(self, token: str):
        auth = get_services(current_app).firebase.auth

        try:
            return auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=10)
        except ValueError as error:
            raise AuthError(
                {"code": "missing_token", "description": str(error)}, 401
            )
        except auth.ExpiredIdTokenError as error:
            raise AuthError(
                {"code": "expired_token", "description": str(error)}, 401
            )
        except auth.RevokedIdTokenError as error:
            raise AuthError(
                {"code": "revoked_token", "description": str(error)}, 401
            )
        except auth.InvalidIdTokenError as error:
            raise AuthError(
                {"code": "invalid_token", "description": str(error)}, 401
            )
        except auth.CertificateFetchError as error:
            raise AuthError(
                {
                    "code": "certificate_fetch_fail",
                    "description": str(error)
                }, 500
            )
        except auth.UserDisabledError as error:
            raise AuthError(
                {"code": "user_disabled", "description": str(error)}, 403
            )


def get_requires_auth(app: Flask):
    """Retrieves the Models extension from a Flask app

    Args:
        app (Flask): flask application

    Returns:
        ModelsExtension: services
    """

    return cast(RequiresAuthExtension, app.extensions[RequiresAuthExtension.KEY])


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        # Depending on environment (test/prod), the output of the get_requires_auth will be either mocked or real functionality
        payload = get_requires_auth(current_app).verify_token(token)
        # g stands for global and tears down as soon as the request is processed
        g.payload = payload

        return f(*args, **kwargs)

    return decorated
