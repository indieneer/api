from datetime import timedelta
from unittest.mock import MagicMock, patch
from flask import Flask, make_response

from flask_cors import CORS

from app.middlewares.cors_middleware import CORSMiddleware, create_cors_handler
from tests.unit_test import UnitTest


class CORSMiddlewareTestCase(UnitTest):

    def setUp(self) -> None:
        self.app = Flask(__name__)

    def test_create_cors_handler(self):
        # given
        origins = ["http://example.com"]
        allow_headers = sorted([
            "Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token",
            "Authorization", "accept", "origin", "Cache-Control", "X-Requested-With"
        ])
        expose_headers = sorted(
            ["Content-Length", "Access-Control-Allow-Origin"]
        )
        supports_credentials = True
        max_age = timedelta(hours=24)
        methods = sorted(["POST", "GET", "PATCH", "PUT", "DELETE"])

        handler = create_cors_handler(CORS(
            origins=origins,
            allow_headers=allow_headers,
            expose_headers=expose_headers,
            supports_credentials=supports_credentials,
            max_age=max_age,
            methods=methods
        ))

        # when
        preflight_headers = {
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": allow_headers
        }
        with self.app.test_request_context("/", method="OPTIONS", headers=preflight_headers):
            mock_response = make_response()
            result = handler(mock_response)

            # then
            self.assertTrue(callable(handler))
            print(result.headers)

            self.assertEqual(
                result.headers.get("Access-Control-Allow-Origin"),
                ", ".join(origins)
            )
            self.assertEqual(
                result.headers.get("Access-Control-Expose-Headers"),
                ", ".join(expose_headers)
            )
            self.assertEqual(
                result.headers.get("Access-Control-Allow-Credentials"),
                str(supports_credentials).lower()
            )
            self.assertEqual(
                result.headers.get("Access-Control-Allow-Headers"),
                ", ".join(allow_headers)
            )
            self.assertEqual(
                result.headers.get("Access-Control-Max-Age"),
                str(int(max_age.total_seconds()))
            )
            self.assertEqual(
                result.headers.get("Access-Control-Allow-Methods"),
                ", ".join(methods)
            )

    @patch("app.middlewares.cors_middleware.create_cors_handler")
    def test_cors_middleware(self, create_cors_handler):
        # given
        origins = ["http://example.com"]

        def cors_handler_side_effect(response):
            response.headers.add("Access-Control-Allow-Origin", origins[0])
            return response
        mock_cors_handler = MagicMock()
        mock_cors_handler.side_effect = cors_handler_side_effect

        create_cors_handler.return_value = mock_cors_handler

        mock_next_handler = MagicMock()
        mock_next_handler.side_effect = lambda _: make_response()

        options = CORS(origins=origins)
        middleware = CORSMiddleware(options)

        # when
        with self.app.test_request_context("/", method="POST") as context:
            response = middleware.dispatch(context.request, mock_next_handler)

            # then
            create_cors_handler.assert_called_once_with(options)
            mock_next_handler.assert_called_once_with(context.request)
            mock_cors_handler.assert_called_once_with(response)
            self.assertEqual(
                response.headers.get("Access-Control-Allow-Origin"),
                origins[0]
            )
