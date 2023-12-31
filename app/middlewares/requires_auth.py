import time
from datetime import datetime, timedelta
from functools import wraps

import requests
from flask import g, current_app
from jose import jwt, exceptions

from . import AuthError, get_token_auth_header
from config import app_config

cache = {"data_json": None, "timestamp": float()}

TEST_SECRET_KEY = "testsecretkey"
TEST_AUTH0_DOMAIN = app_config["AUTH0_DOMAIN"]
TEST_AUTH0_AUDIENCE = app_config["AUTH0_AUDIENCE"]
TEST_AUTH0_NAMESPACE = app_config["AUTH0_NAMESPACE"]

def create_test_token(profile_id: str, idp_id='auth0|1', roles: list[str] | None=None):
    """Used for unit testing
    """

    if roles is None:
        roles = []

    return jwt.encode(
        {
            "sub": idp_id,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
            "scope": [],
            f"{TEST_AUTH0_NAMESPACE}/profile_id": profile_id,
            f"{TEST_AUTH0_NAMESPACE}/roles": [role.capitalize() for role in roles],
            "aud": TEST_AUTH0_AUDIENCE,
            "iss": "https://" + TEST_AUTH0_DOMAIN + "/"
        },
        TEST_SECRET_KEY,
        algorithm="HS256"
    )


def mocked_requires_auth(f):
    """Used for unit testing
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()

        payload = jwt.decode(
            token,
            TEST_SECRET_KEY,
            algorithms=["HS256"],
            audience=TEST_AUTH0_AUDIENCE,
            issuer=f"https://{TEST_AUTH0_DOMAIN}/"
        )

        g.payload = payload

        return f(*args, **kwargs)

    return decorated


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        # Use mocked wrapper for test purposes
        if current_app.testing:
            return mocked_requires_auth(f)(*args, **kwargs)

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
