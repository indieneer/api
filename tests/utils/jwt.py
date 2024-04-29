from datetime import datetime, timedelta
from typing import Dict
from bson import ObjectId
from jose import jwt

from app.middlewares.requires_auth import RequiresAuthExtension
from app.middlewares.requires_role import RequiresRoleExtension

TEST_AUTH_SECRET_KEY = "testsecretkey"
TEST_AUTH_DOMAIN = "identitytoolkit.google.com"
TEST_AUTH_AUDIENCE = "https://api.indieneer.com"
TEST_AUTH_NAMESPACE = "https://indieneer.com"


def create_test_token(profile_id: str, idp_id: str | None = None, roles: list[str] | None = None, permissions: list[str] | None = None):
    """Used for unit testing
    """

    if roles is None:
        roles = []

    return jwt.encode(
        {
            "sub": idp_id or str(ObjectId),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
            "scope": [],
            f"{TEST_AUTH_NAMESPACE}/profile_id": profile_id,
            f"{TEST_AUTH_NAMESPACE}/roles": [role.capitalize() for role in roles],
            f"{TEST_AUTH_NAMESPACE}/permissions": permissions or [],
            "aud": TEST_AUTH_AUDIENCE,
            "iss": "https://" + TEST_AUTH_DOMAIN + "/"
        },
        TEST_AUTH_SECRET_KEY,
        algorithm="HS256"
    )


class MockRequiresAuthExtension(RequiresAuthExtension):
    def verify_token(self, token: str):
        return jwt.decode(
            token,
            TEST_AUTH_SECRET_KEY,
            algorithms=["HS256"],
            audience=TEST_AUTH_AUDIENCE,
            issuer=f"https://{TEST_AUTH_DOMAIN}/"
        )


class MockRequiresRoleExtension(RequiresRoleExtension):
    def verify_role(self, payload: Dict, role: str):
        roles = payload.get(f"{TEST_AUTH_NAMESPACE}/roles", [])

        return role.capitalize() in roles
