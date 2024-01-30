from enum import Enum
from os import environ as env


class FirebaseRole(Enum):
    Admin = "Admin"
    User = "User"
