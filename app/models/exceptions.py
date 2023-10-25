class IndieneerBaseException(Exception):

    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message = message


class NotFoundException(IndieneerBaseException):
    def __init__(self, model_name: str) -> None:
        super().__init__(f"\"{model_name}\" not found.")


class ForbiddenException(IndieneerBaseException):
    def __init__(self) -> None:
        super().__init__("Forbidden.")
