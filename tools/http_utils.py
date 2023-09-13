from typing import Any, Dict


def respond_success(data: Any, meta: Dict = None, status_code: int = 200):
    response_object = {
        "status": "ok",
        "data": data,
    }

    response_object |= {"meta": meta} if meta is not None else {}

    return response_object, status_code


def respond_error(error: str, status_code: int = 400):
    response_object = {
        "status": "error",
        "error": error,
    }

    return response_object, status_code


def respond_not_found(error: str, status_code: int = 404):
    response_object = {
        "status": "not found",
        "error": error
    }

    return response_object, status_code


if __name__ == "__main__":
    print(respond_success({"person": {"name": "Christiano Ronaldo", "age": 0}, "privilege": "admin futbola"},
                          {"page": 10}))
