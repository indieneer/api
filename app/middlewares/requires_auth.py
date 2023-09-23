import time
from functools import wraps

import requests
from flask import g
from jose import jwt, exceptions

from . import AuthError, get_token_auth_header
from config import app_config

cache = {"data_json": None, "timestamp": float()}


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
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

        token = get_token_auth_header()
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

            # g stands for global and tears down as soon as the request is processed
            g.payload = payload

            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)

    return decorated
