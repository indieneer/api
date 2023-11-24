from app.models.exceptions import IndieneerBaseException


class BadRequestException(IndieneerBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnprocessableEntityException(IndieneerBaseException):
    def __init__(self, message: str = "Bad Request.") -> None:
        super().__init__(message)


class InternalServerErrorException(IndieneerBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)