from enum import Enum
from os import environ as env


class Auth0Role(Enum):
    Admin = "Admin"
    User = "User"


AUTH0_ROLES: dict[str, str] = {
    key: value for
    key, value in
    [x.split(':') for x in env.get("AUTH0_ROLES", "").split(',')]
}
