from typing import Any, Dict, Optional


def respond_success(data: Any, meta: Optional[Dict] = None, status_code: int = 200):
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
