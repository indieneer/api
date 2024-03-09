class InvalidLoginCredentialsException(Exception):
    pass


class ErrorDecodeException(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"Failed to decode Firebase error \"{code}\"")


class NotFoundException(Exception):
    def __init__(self, what: str) -> None:
        super().__init__(f"\"{what}\" not found.")


class UnknownException(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"Request failed with code \"{code}\"")


exceptions_mapping: dict[str, type[Exception]] = {
    "INVALID_LOGIN_CREDENTIALS": InvalidLoginCredentialsException,
}
