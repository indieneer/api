from dataclasses import dataclass
from typing import Callable, Optional, Any, Dict
import time
import math
import uuid
import json
from datetime import datetime

from flask_http_middleware import BaseHTTPMiddleware
from flask import Request, Response
from .logger import Logger


@dataclass
class LoggerOptions:
    with_response_body: Optional[Callable[[Request], bool]] = None
    with_request_body: Optional[Callable[[Request], bool]] = None
    with_request_id: Optional[bool] = None
    custom_attributes: Optional[Dict[str, Any]] = None

REQUEST_BODY_MAX_SIZE = 64 * 1024 # KB
RESPONSE_BODY_MAX_SIZE = 64 * 1024 # KB

class LoggerMiddleware(BaseHTTPMiddleware):
    logger: Logger
    options: LoggerOptions

    def __init__(self, logger: Logger, options: LoggerOptions):
        super().__init__()

        self.logger = logger
        self.options = options

    def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:
        attributes = {}

        attributes["request.method"] = request.method
        attributes["request.path"] = request.path
        attributes["request.user_agent"] = request.user_agent.string
        attributes["request.ip"] = request.remote_addr
        attributes["request.started_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        start_time = time.time()
        response = call_next(request)
        latency = (time.time() - start_time) * 1000

        if self.options.with_request_id:
            request_id = str(uuid.uuid4())
            response.headers.add("X-Request-Id", request_id)
            attributes["request.id"] = request_id

        attributes["request.finished_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        attributes["response.latency"] = math.floor(latency)
        attributes["response.status"] = response.status_code

        if self.options.custom_attributes:
            attributes |= self.options.custom_attributes
            
        if self.options.with_request_body and self.options.with_request_body(request):
            request_body = request.data[:REQUEST_BODY_MAX_SIZE].decode("utf8")

            try:
                attributes["request.body"] = json.dumps(json.loads(request_body), indent=None)
            except:
                attributes["request.body"] = request_body

            attributes["request.length"] = len(request.data)

        if self.options.with_response_body and self.options.with_response_body(request):
            response_body = response.data[:RESPONSE_BODY_MAX_SIZE].decode("utf8")

            try:
                attributes["response.body"] = json.dumps(json.loads(response_body), indent=None)
            except:
                attributes["response.body"] = response_body

            attributes["response.length"] = len(response.data)

        msg = " ".join([f"{attribute}={value}" for (attribute, value) in attributes.items()])
        if response.status_code >= 400 and response.status_code < 500:
            self.logger.warn(msg)
        elif response.status_code >= 500:
            self.logger.error(msg)
        else:
            self.logger.info(msg)

        return response