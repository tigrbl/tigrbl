from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

from tigrbl_concrete._concrete._response import Response


TIGRBL_LENS_VERSION = "latest"
TIGRBL_LENS_CSS_URL = f"https://esm.sh/@tigrbljs/tigrbl-lens@{TIGRBL_LENS_VERSION}/dist/tigrbl-lens.css?css"


def _with_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def _build_docs_config(router: Any, *, spec_path: str) -> list[dict[str, Any]]:
    openapi_path = _with_leading_slash(str(getattr(router, "openapi_url", "/openapi.json") or "/openapi.json"))
    openrpc_path = _with_leading_slash(str(spec_path or getattr(router, "openrpc_path", "/openrpc.json") or "/openrpc.json"))
    return [
        {"id": "rest", "label": "REST", "kind": "openapi", "url": openapi_path, "rawSpecHref": openapi_path, "protocols": ["rest"]},
        {"id": "jsonrpc", "label": "JSON-RPC", "kind": "openrpc", "url": openrpc_path, "rawSpecHref": openrpc_path, "protocols": ["jsonrpc"]},
    ]


def build_lens_html(router: Any, request: Any, *, spec_path: str) -> str:
    base = (getattr(request, "script_name", "") or "").rstrip("/")
    route_prefix = str(getattr(router, "_tigrbl_route_prefix", "") or "").rstrip("/")
    spec_url = f"{base}{route_prefix}{_with_leading_slash(spec_path)}"
    quoted_spec_url = quote(spec_url, safe="/:?=&%")
    docs_config = json.dumps(_build_docs_config(router, spec_path=spec_path), separators=(",", ":"))
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{router.title} — Lens</title>
    <link
      rel="stylesheet"
      href="{TIGRBL_LENS_CSS_URL}"
    />
    <style>
      html, body, #root {{
        margin: 0;
        width: 100%;
        min-height: 100%;
      }}
      body {{
        min-height: 100vh;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="importmap">
      {{
        "imports": {{
          "react": "https://esm.sh/react@19",
          "react-dom/client": "https://esm.sh/react-dom@19/client",
          "@tigrbljs/tigrbl-lens": "https://esm.sh/@tigrbljs/tigrbl-lens@{TIGRBL_LENS_VERSION}"
        }}
      }}
    </script>
    <script type="module">
      import React from "react";
      import {{ createRoot }} from "react-dom/client";
      import {{ EmbeddedLens }} from "@tigrbljs/tigrbl-lens";

      const rootEl = document.getElementById("root");
      if (rootEl) {{
        createRoot(rootEl).render(
          React.createElement(
            React.StrictMode,
            null,
            React.createElement(EmbeddedLens, {{ url: "{quoted_spec_url}", docs: {docs_config} }}),
          ),
        );
      }}
    </script>
  </body>
</html>
"""


def mount_lens(
    router: Any,
    *,
    path: str = "/lens",
    name: str = "__lens__",
    spec_path: str | None = None,
) -> Any:
    """Mount a tigrbl-lens HTML endpoint onto ``router``."""

    resolved_spec_path = spec_path or getattr(router, "openrpc_path", "/openrpc.json")
    resolved_spec_path = _with_leading_slash(resolved_spec_path)

    def _lens_handler(request: Any) -> Response:
        return Response.html(
            build_lens_html(router, request, spec_path=resolved_spec_path)
        )

    router.add_route(
        path,
        _lens_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
        inherit_owner_dependencies=False,
    )
    return router


__all__ = ["build_lens_html", "mount_lens"]
