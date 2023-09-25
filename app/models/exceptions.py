class BaseException(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)

        self.status_code = status_code
        self.message = message


class NotFoundException(BaseException):
    def __init__(self, model_name: str) -> None:
        super().__init__(404, f"\"{model_name}\" not found.")
