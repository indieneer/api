import time
from functools import wraps
from typing import cast

import requests
from flask import Flask, g, current_app
from jose import jwt, exceptions

from . import AuthError, get_token_auth_header
from config import app_config

cache = {"data_json": None, "timestamp": float()}

class RequiresAuthExtension:
    """Workaround to inject custom JWT validator for unit testing
    """
    
    KEY = "requires_auth"

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self

    def verify_token(self, token: str):
        AUTH0_DOMAIN = app_config["AUTH0_DOMAIN"]
        AUTH0_AUDIENCE = app_config["AUTH0_AUDIENCE"]

        # self-implemented caching, if we're going to need more functionalities we can use the 'requests-cache' package
        # seconds
        if cache["data_json"] is None or (time.time() - cache["timestamp"]) > 3600:
            data_json = requests.get(
                "https://" + AUTH0_DOMAIN + "/.well-known/jwks.json").json()
            cache["data_json"] = data_json
            cache["timestamp"] = time.time()
        else:
            data_json = cache["data_json"]

        jwks = data_json
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=AUTH0_AUDIENCE,
                    issuer="https://" + AUTH0_DOMAIN + "/"
                )
            except exceptions.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except exceptions.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            return payload
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    
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
