class InvalidLoginCredentialsException(Exception):
    pass


class TokenExpiredException(Exception):
    pass


class UserDisabledException(Exception):
    pass


class NotFoundException(Exception):
    def __init__(self, what: str) -> None:
        super().__init__(f"\"{what}\" not found.")


class InvalidApiKeyException(Exception):
    pass


class InvalidRefreshTokenException(Exception):
    pass


class InvalidJsonPayloadReceivedException(Exception):
    pass


class InvalidGrantTypeException(Exception):
    pass


class MissingRefreshTokenException(Exception):
    pass


class UnknownException(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"Request failed with code \"{code}\"")


class ErrorDecodeException(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"Failed to decode Firebase error \"{code}\"")


exceptions_mapping: dict[str, type[Exception]] = {
    # secure token
    "TOKEN_EXPIRED": TokenExpiredException,
    "USER_DISABLED": UserDisabledException,
    "USER_NOT_FOUND": NotFoundException,
    # "InvalidApiKeyException": InvalidApiKeyException,
    "INVALID_REFRESH_TOKEN": InvalidRefreshTokenException,
    # "InvalidJsonPayloadReceivedException": InvalidJsonPayloadReceivedException,
    "INVALID_GRANT_TYPE": InvalidGrantTypeException,
    "MISSING_REFRESH_TOKEN": MissingRefreshTokenException,

    # identity toolkit
    "INVALID_LOGIN_CREDENTIALS": InvalidLoginCredentialsException,
}
