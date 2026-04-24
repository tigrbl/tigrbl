from __future__ import annotations

import argparse
import json
import re
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from app_spec import build_rust_payload, compose_app_spec
from tigrbl_runtime import Runtime, compiled_extension_available


USER_ID_PATTERN = re.compile(r"^/users/(?P<id>[^/]+)$")
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#111827"/>
  <path d="M18 16h28v8H36v24h-8V24H18z" fill="#f8fafc"/>
</svg>
"""

APP_SPEC = compose_app_spec()
RUST_PAYLOAD = build_rust_payload()
RUNTIME = Runtime(executor_backend="rust")
RUST_HANDLE = RUNTIME.rust_handle(APP_SPEC)


USER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
    },
    "required": ["id", "name"],
}


def build_openapi_document() -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": APP_SPEC.title,
            "version": APP_SPEC.version,
            "description": APP_SPEC.description,
        },
        "paths": {
            "/healthz": {
                "get": {
                    "operationId": "healthz",
                    "summary": "Rust runtime demo health",
                    "responses": {"200": {"description": "Runtime status"}},
                }
            },
            "/users": {
                "post": {
                    "operationId": "users.create",
                    "summary": "Create a demo user through the Rust runtime",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": USER_SCHEMA}},
                    },
                    "responses": {
                        "200": {
                            "description": "Created user",
                            "content": {"application/json": {"schema": USER_SCHEMA}},
                        }
                    },
                }
            },
            "/users/{id}": {
                "get": {
                    "operationId": "users.read",
                    "summary": "Read a demo user through the Rust runtime",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User",
                            "content": {"application/json": {"schema": USER_SCHEMA}},
                        },
                        "404": {"description": "User not found"},
                    },
                }
            },
        },
        "components": {"schemas": {"User": USER_SCHEMA}},
        "x-tigrbl": {
            "executor": "rust",
            "runtime": RUST_HANDLE.describe(),
            "compiled_extension_available": compiled_extension_available(),
            "rust_payload": RUST_PAYLOAD,
        },
    }


def build_openrpc_document() -> dict[str, Any]:
    return {
        "openrpc": "1.3.2",
        "info": {
            "title": f"{APP_SPEC.title} JSON-RPC",
            "version": APP_SPEC.version,
            "description": APP_SPEC.description,
        },
        "methods": [
            {
                "name": "users.create",
                "summary": "Create a demo user through the Rust runtime",
                "params": [
                    {
                        "name": "id",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "name",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
                "result": {"name": "user", "schema": USER_SCHEMA},
            },
            {
                "name": "users.read",
                "summary": "Read a demo user through the Rust runtime",
                "params": [
                    {
                        "name": "id",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "result": {"name": "user", "schema": USER_SCHEMA},
            },
        ],
        "components": {"schemas": {"User": USER_SCHEMA}},
        "x-tigrbl": {
            "executor": "rust",
            "runtime": RUST_HANDLE.describe(),
            "compiled_extension_available": compiled_extension_available(),
        },
    }


def build_swagger_page() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{APP_SPEC.title} Swagger UI</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.31.0/swagger-ui.css">
  <style>.swagger-ui .topbar {{ display: none; }}</style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.31.0/swagger-ui-bundle.js"></script>
  <script src="https://unpkg.com/swagger-ui-dist@5.31.0/swagger-ui-standalone-preset.js"></script>
  <script>
    console.info("tigrbl rust runtime swagger ui", {{ spec: "/openapi.json" }});
    window.onload = function () {{
      window.ui = SwaggerUIBundle({{
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        layout: "StandaloneLayout"
      }});
    }};
  </script>
</body>
</html>
"""


def build_lens_page() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{APP_SPEC.title} Lens UI</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="https://esm.sh/@tigrbljs/tigrbl-lens@latest/dist/tigrbl-lens.css?css">
  <style>html, body, #root {{ margin: 0; width: 100%; min-height: 100%; }} body {{ min-height: 100vh; }}</style>
</head>
<body>
  <div id="root"></div>
  <script type="importmap">
    {{
      "imports": {{
        "react": "https://esm.sh/react@19",
        "react-dom/client": "https://esm.sh/react-dom@19/client",
        "@tigrbljs/tigrbl-lens": "https://esm.sh/@tigrbljs/tigrbl-lens@latest"
      }}
    }}
  </script>
  <script type="module">
    import React from "react";
    import {{ createRoot }} from "react-dom/client";
    import {{ EmbeddedLens }} from "@tigrbljs/tigrbl-lens";

    console.info("tigrbl rust runtime lens ui", {{ spec: "/openrpc.json" }});
    const rootEl = document.getElementById("root");
    if (rootEl) {{
      createRoot(rootEl).render(
        React.createElement(
          React.StrictMode,
          null,
          React.createElement(EmbeddedLens, {{ url: "/openrpc.json" }}),
        ),
      );
    }}
  </script>
</body>
</html>
"""


def build_console_page() -> str:
    example = (
        'curl -s -X POST -H "Content-Type: application/json" '
        "--data '{\"id\":\"u1\",\"name\":\"Ada\"}' http://127.0.0.1:8765/users"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{APP_SPEC.title} Runtime Console</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5; }}
    code, pre {{ background: #f5f5f5; border-radius: 4px; padding: .2rem .35rem; }}
    pre {{ padding: 1rem; overflow-x: auto; }}
    a {{ color: #0645ad; }}
  </style>
</head>
<body>
  <h1>{APP_SPEC.title} Runtime Console</h1>
  <p>Python-authored Tigrbl AppSpec served through <code>Runtime(executor_backend="rust")</code>.</p>
  <ul>
    <li><a href="/healthz">/healthz</a></li>
    <li><a href="/openapi.json">/openapi.json</a></li>
    <li><a href="/openrpc.json">/openrpc.json</a></li>
    <li><a href="/docs">/docs</a></li>
    <li><a href="/lens">/lens</a></li>
    <li><a href="/console">/console</a></li>
    <li><a href="/favicon.svg">/favicon.svg</a></li>
  </ul>
  <h2>Try it</h2>
  <pre>{example}</pre>
  <script>
    console.info("tigrbl rust runtime console", {{ executor: "rust" }});
  </script>
</body>
</html>
"""


class RustRuntimeDemoHandler(BaseHTTPRequestHandler):
    server_version = "tigrbl-rust-runtime-demo/0.2"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/healthz":
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

        if path == "/openapi.json":
            self._write_json(HTTPStatus.OK, build_openapi_document())
            return

        if path == "/openrpc.json":
            self._write_json(HTTPStatus.OK, build_openrpc_document())
            return

        if path == "/docs":
            self._write_html(HTTPStatus.OK, build_swagger_page())
            return

        if path == "/swagger":
            self.send_response(HTTPStatus.TEMPORARY_REDIRECT)
            self.send_header("Location", "/docs")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if path == "/console":
            self._write_html(HTTPStatus.OK, build_console_page())
            return

        if path in {"/lens", "/rdocs"}:
            self._write_html(HTTPStatus.OK, build_lens_page())
            return

        if path == "/favicon.svg":
            self._write_text(HTTPStatus.OK, FAVICON_SVG, content_type="image/svg+xml")
            return

        if path == "/favicon.ico":
            self.send_response(HTTPStatus.TEMPORARY_REDIRECT)
            self.send_header("Location", "/favicon.svg")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        match = USER_ID_PATTERN.match(path)
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

        self._write_json(HTTPStatus.NOT_FOUND, {"error": f"unknown route {path}"})

    def do_POST(self) -> None:  # noqa: N802
        payload = self._read_json_body()
        if payload is None:
            return

        path = urlparse(self.path).path
        if path == "/users":
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

        if path == "/rpc":
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

        self._write_json(HTTPStatus.NOT_FOUND, {"error": f"unknown route {path}"})

    def log_message(self, format: str, *args: Any) -> None:
        message = format % args if args else format
        self._log_event("http.request", message=message)

    def _log_event(self, event: str, **fields: Any) -> None:
        payload = {
            "event": event,
            "client": self.client_address[0] if self.client_address else None,
            "request": self.requestline,
            **fields,
        }
        sys.stderr.write(json.dumps(payload, sort_keys=True) + "\n")
        sys.stderr.flush()

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

    def _write_html(self, status: int, payload: str) -> None:
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_text(self, status: int, payload: str, *, content_type: str) -> None:
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
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
