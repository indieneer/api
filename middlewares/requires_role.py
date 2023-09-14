from functools import wraps


def requires_role(f, role: str):
    """Determines if the Admin role in the validated token exists
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        pass
        # TODO Parse the "role" field from claims and check if it's equal to "admin"

    return decorated
