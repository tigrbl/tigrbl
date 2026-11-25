"""Mount the ZDoc viewer over existing documentation payloads."""

from __future__ import annotations

import json
from html import escape
from typing import Any
from urllib.parse import quote, urlsplit

from tigrbl_concrete._concrete._response import Response

TIGRBL_ZDOC_VERSION = "0.1.1"
_PACKAGE = "@tigrbljs/tigrbl-zdoc"
_CDN = f"https://esm.sh/{_PACKAGE}@{TIGRBL_ZDOC_VERSION}"


def _public_url(request: Any, router: Any, path: str) -> str:
    if urlsplit(path).scheme in {"http", "https"}:
        return path
    base = (getattr(request, "script_name", "") or "").rstrip("/")
    prefix = (getattr(router, "_tigrbl_route_prefix", "") or "").rstrip("/")
    return quote(f"{base}{prefix}/{path.lstrip('/')}", safe="/:?=&%")


def build_zdoc_html(
    router: Any,
    request: Any,
    *,
    spec_path: str | None = None,
    openapi_path: str | None = None,
    asyncapi_path: str | None = None,
    title: str | None = None,
    unwrap_rpc_params: bool = True,
) -> str:
    sources = [
        ("rest", "REST", "openapi", openapi_path or getattr(router, "openapi_url", None) or "/openapi.json"),
        ("jsonrpc", "JSON-RPC", "openrpc", spec_path or getattr(router, "openrpc_path", None) or "/openrpc.json"),
        ("websocket", "WebSocket", "asyncapi", asyncapi_path),
    ]
    docs = []
    for identifier, label, kind, path in sources:
        if not path:
            continue
        url = _public_url(request, router, path)
        docs.append({
            "id": identifier, "label": label, "kind": kind,
            "url": url, "rawSpecHref": url, "protocols": [identifier],
        })
        if kind == "openrpc" and unwrap_rpc_params:
            docs[-1]["unwrapRpcParams"] = True
    props = json.dumps({"docs": docs}, separators=(",", ":")).replace("<", r"\u003c")
    page_title = escape(title or str(router.title))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{page_title} — ZDoc</title>
  <link rel="stylesheet" href="{_CDN}/dist/tigrbl-zdoc.css?css" />
  <style>html, body, #root {{ margin: 0; min-height: 100%; }}</style>
  <script type="importmap">
    {{"imports": {{"react": "https://esm.sh/react@19.2.4",
                  "react-dom/client": "https://esm.sh/react-dom@19.2.4/client?external=react",
                  "{_PACKAGE}": "{_CDN}?external=react,react-dom"}}}}
  </script>
</head>
<body>
  <div id="root"></div>
  <script type="module">
    import React from "react";
    import {{ createRoot }} from "react-dom/client";
    import {{ EmbeddedZDoc }} from "{_PACKAGE}";
    createRoot(document.getElementById("root")).render(
      React.createElement(EmbeddedZDoc, {props})
    );
  </script>
</body>
</html>
"""


def mount_zdoc(
    router: Any,
    *,
    path: str = "/zdoc",
    name: str = "__zdoc__",
    spec_path: str | None = None,
    openapi_path: str | None = None,
    asyncapi_path: str | None = None,
    title: str | None = None,
    unwrap_rpc_params: bool = True,
) -> Any:
    """Mount ZDoc over application-owned documentation payloads.

    Disable unwrap_rpc_params when the OpenRPC document declares named
    parameters directly instead of Tigrbl’s single request descriptor.
    """

    def handler(request: Any) -> Response:
        return Response.html(
            build_zdoc_html(
                router, request, spec_path=spec_path, openapi_path=openapi_path,
                asyncapi_path=asyncapi_path, title=title, unwrap_rpc_params=unwrap_rpc_params,
            )
        )

    router.add_route(
        path, handler, methods=["GET"], name=name, include_in_schema=False,
        inherit_owner_dependencies=False,
    )
    return router


__all__ = ["build_zdoc_html", "mount_zdoc"]
