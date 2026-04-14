from __future__ import annotations

import argparse
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from app_spec import build_rust_payload, compose_app_spec
from tigrbl_runtime import Runtime, compiled_extension_available


USER_ID_PATTERN = re.compile(r"^/users/(?P<id>[^/]+)$")

APP_SPEC = compose_app_spec()
RUST_PAYLOAD = build_rust_payload()
RUNTIME = Runtime(executor_backend="rust")
RUST_HANDLE = RUNTIME.rust_handle(APP_SPEC)


class RustRuntimeDemoHandler(BaseHTTPRequestHandler):
    server_version = "tigrbl-rust-runtime-demo/0.2"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._write_json(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "app": APP_SPEC.title,
                    "compiled_extension_available": compiled_extension_available(),
                    "executor": "rust",
                    "runtime": RUST_HANDLE.describe(),
                },
            )
            return

        match = USER_ID_PATTERN.match(self.path)
        if match:
            response = RUST_HANDLE.execute_rest(
                {
                    "operation": "users.read",
                    "transport": "rest",
                    "path": "/users/{id}",
                    "method": "GET",
                    "path_params": {"id": match.group("id")},
                }
            )
            self._write_runtime_response(response)
            return

        self._write_json(HTTPStatus.NOT_FOUND, {"error": f"unknown route {self.path}"})

    def do_POST(self) -> None:  # noqa: N802
        payload = self._read_json_body()
        if payload is None:
            return

        if self.path == "/users":
            response = RUST_HANDLE.execute_rest(
                {
                    "operation": "users.create",
                    "transport": "rest",
                    "path": "/users",
                    "method": "POST",
                    "body": payload,
                }
            )
            self._write_runtime_response(response)
            return

        if self.path == "/rpc":
            method = str(payload.get("method", ""))
            params = payload.get("params") or {}
            if method == "users.create":
                envelope = {
                    "operation": "users.create",
                    "transport": "jsonrpc",
                    "path": "/rpc",
                    "method": "POST",
                    "body": params,
                }
            elif method == "users.read":
                envelope = {
                    "operation": "users.read",
                    "transport": "jsonrpc",
                    "path": "/rpc",
                    "method": "POST",
                    "path_params": {"id": params.get("id")},
                }
            else:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "jsonrpc": "2.0",
                        "id": payload.get("id"),
                        "error": {"code": -32601, "message": f"unknown method {method}"},
                    },
                )
                return

            response = RUST_HANDLE.execute_jsonrpc(envelope)
            if int(response["status"]) >= 400:
                self._write_json(
                    HTTPStatus.OK,
                    {
                        "jsonrpc": "2.0",
                        "id": payload.get("id"),
                        "error": {
                            "code": response["status"],
                            "message": response["body"],
                        },
                    },
                )
                return

            self._write_json(
                HTTPStatus.OK,
                {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "result": response["body"],
                },
            )
            return

        self._write_json(HTTPStatus.NOT_FOUND, {"error": f"unknown route {self.path}"})

    def log_message(self, format: str, *args: Any) -> None:
        del format, args
        return

    def _read_json_body(self) -> dict[str, Any] | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": f"invalid json: {exc.msg}"})
            return None
        if not isinstance(payload, dict):
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "request body must be a JSON object"})
            return None
        return payload

    def _write_runtime_response(self, response: dict[str, Any]) -> None:
        self._write_json(int(response["status"]), response["body"], headers=response.get("headers"))

    def _write_json(
        self,
        status: int,
        payload: Any,
        *,
        headers: dict[str, Any] | None = None,
    ) -> None:
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        for key, value in (headers or {}).items():
            self.send_header(str(key), str(value))
        self.end_headers()
        self.wfile.write(encoded)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve a Python-authored Tigrbl AppSpec via the Rust runtime."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = HTTPServer((args.host, args.port), RustRuntimeDemoHandler)
    print(
        json.dumps(
            {
                "host": args.host,
                "port": args.port,
                "app": RUST_PAYLOAD,
                "executor": "rust",
                "compiled_extension_available": compiled_extension_available(),
                "runtime": RUST_HANDLE.describe(),
            },
            sort_keys=True,
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
