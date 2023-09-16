from functools import wraps
from flask import g

from config import configuration
from middlewares import AuthError


def requires_role(role: str):
    """Determines if the Admin role in the validated token exists"""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            payload = g.get('payload')
            roles = payload.get(configuration.get("AUTH0_NAMESPACE") + "/roles")
            if role.capitalize() in roles:
                return f(*args, **kwargs)
            else:
                raise AuthError("no permission", 403)

        return decorated

    return decorator
