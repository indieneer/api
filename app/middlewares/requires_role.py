from functools import wraps
from typing import Dict, cast
from flask import Flask, current_app, g

from config import app_config
from app.middlewares import AuthError
from lib.http_utils import respond_error

class RequiresRoleExtension:
    """Workaround to inject custom JWT validator for unit testing
    """
    
    KEY = "requires_role"

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self
        
    def verify_role(self, payload: Dict, role: str):
        roles = payload.get(app_config["AUTH0_NAMESPACE"] + "/roles", [])

        return role.capitalize() in roles

def get_requires_role(app: Flask):
    """Retrieves the Models extension from a Flask app

    Args:
        app (Flask): flask application

    Returns:
        ModelsExtension: services
    """

    return cast(RequiresRoleExtension, app.extensions[RequiresRoleExtension.KEY])

def requires_role(role: str):
    """Determines if the Admin role in the validated token exists"""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            payload = g.get('payload')
            if not payload:
                return respond_error("missing decoded user", 500)

            if get_requires_role(current_app).verify_role(payload, role):
                return f(*args, **kwargs)
            else:
                raise AuthError("no permission", 403)

        return decorated

    return decorator
