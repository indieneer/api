from datetime import datetime, timedelta
from typing import Dict
from jose import jwt

from app.middlewares.requires_auth import RequiresAuthExtension
from app.middlewares.requires_role import RequiresRoleExtension

TEST_SECRET_KEY = "testsecretkey"
TEST_AUTH0_DOMAIN = "indieneer.eu.auth0.com"
TEST_AUTH0_AUDIENCE = "https://api.indieneer.com"
TEST_AUTH0_NAMESPACE = "https://indieneer.com"


def create_test_token(profile_id: str, idp_id='auth0|1', roles: list[str] | None = None):
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


class MockRequiresAuthExtension(RequiresAuthExtension):
    def verify_token(self, token: str):
        return jwt.decode(
            token,
            TEST_SECRET_KEY,
            algorithms=["HS256"],
            audience=TEST_AUTH0_AUDIENCE,
            issuer=f"https://{TEST_AUTH0_DOMAIN}/"
        )


class MockRequiresRoleExtension(RequiresRoleExtension):
    def verify_role(self, payload: Dict, role: str):
        roles = payload.get(TEST_AUTH0_NAMESPACE + "/roles", [])

        return role.capitalize() in roles
