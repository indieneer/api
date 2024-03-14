from typing import TypeVar

from urllib3 import BaseHTTPResponse

from .exceptions import (ErrorDecodeException, UnknownException,
                         exceptions_mapping)

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
