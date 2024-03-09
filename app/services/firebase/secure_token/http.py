from typing import TypeVar

from urllib3 import BaseHTTPResponse

from app.services.firebase.identity_toolkit.exceptions import \
    ErrorDecodeException

from .exceptions import UnknownException, exceptions_mapping


class Request:
    def to_json(self):
        raise Exception("Not implemented.")


class ExchangeRefreshTokenRequest(Request):
    grant_type: str
    refresh_token: str

    def __init__(self, grant_type: str, /, *, refresh_token: str) -> None:
        super().__init__()

        self.grant_type = grant_type
        self.refresh_token = refresh_token

    def to_json(self):
        return {
            "grant_type": self.grant_type,
            "refresh_token": self.refresh_token
        }


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
