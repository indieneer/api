

from typing import TypeVar

from urllib3 import BaseHTTPResponse

from .dto import FirebaseUser
from .exceptions import (ErrorDecodeException, UnknownException,
                         exceptions_mapping)


class Request:
    def to_json(self):
        raise Exception("Not implemented.")


class SignInWithPasswordRequest(Request):
    email: str
    password: str
    return_secure_token: bool

    def __init__(self, email: str, password: str, /, *, return_secure_token: bool = True) -> None:
        super().__init__()

        self.email = email
        self.password = password
        self.return_secure_token = return_secure_token

    def to_json(self):
        return {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": self.return_secure_token,
        }


class SignInWithCustomTokenRequest(Request):
    token: str
    return_secure_token: bool

    def __init__(self, token: str, /, *, return_secure_token: bool = True) -> None:
        super().__init__()

        self.token = token
        self.return_secure_token = return_secure_token

    def to_json(self):
        return {
            "token": self.token,
            "returnSecureToken": self.return_secure_token,
        }


class LookupRequest(Request):
    id_token: str

    def __init__(self, id_token: str, /) -> None:
        super().__init__()

        self.id_token = id_token

    def to_json(self):
        return {
            "idToken": self.id_token,
        }


class LookupResponse:
    users: list[FirebaseUser]

    def __init__(self, response: dict, /) -> None:
        self.users = [FirebaseUser(x) for x in response["users"]]


T = TypeVar('T')


def inflate_response(response: BaseHTTPResponse, cls: type[T]) -> T | Exception:
    if response.status < 200 or response.status >= 500:
        return UnknownException(response.status)

    if response.status >= 200 and response.status < 300:
        data = response.json()

        return cls(**data)

    data = response.json()
    if not ("error" in data and "message" in data["error"]):
        return UnknownException(response.status)

    exception_code = data["error"]["message"]
    exception = exceptions_mapping.get(exception_code)
    if exception is None:
        return ErrorDecodeException(exception_code)

    return exception(exception_code)
