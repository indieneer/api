from functools import wraps
from flask import g

from app.middlewares import AuthError
from lib.http_utils import respond_error


def requires_service_account(f):
    """Decorator to require a service account to access an endpoint"""

    @wraps(f)
    def decorated(*args, **kwargs):
        sub = g.get("payload").get("sub")
        if not sub:
            return respond_error("missing decoded user", 500)

        if "@" in sub and sub.split("@")[1] == "clients":
            return f(*args, **kwargs)
        else:
            raise AuthError("no permission", 403)

    return decorated
