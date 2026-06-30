from __future__ import annotations

import inspect
import logging
from collections.abc import Iterable, Mapping
from typing import Any, Callable, Optional

from tigrbl_concrete._concrete import Request
from tigrbl_concrete._concrete.dependencies import Depends
from tigrbl_concrete._concrete import JSONResponse
from tigrbl_concrete._concrete._response import Response
from .utils import maybe_execute

logger = logging.getLogger(__name__)

_NO_DB_WARNING = "db-not-configured"
_UNAVAILABLE_WARNING = "db-unavailable"


def _resolve_db(candidate: Any) -> Any:
    """Resolve a DB-like object from either a DB handle or a Request object."""
    if hasattr(candidate, "execute"):
        return candidate

    state = getattr(candidate, "state", None)
    db = getattr(state, "db", None)
    if db is not None:
        return db
    return None


def _has_execute(candidate: Any) -> bool:
    return callable(getattr(candidate, "execute", None))


def _query_value(request: Any, name: str, default: str | None = None) -> str | None:
    getter = getattr(request, "query_param", None)
    if callable(getter):
        return getter(name, default)
    query = getattr(request, "query", None) or {}
    values = query.get(name)
    if isinstance(values, (list, tuple)) and values:
        return str(values[0])
    if values is not None:
        return str(values)
    return default


def _query_flag(request: Any, name: str) -> bool:
    value = _query_value(request, name)
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on", "warn"}


def _wants_all_dbs(request: Any) -> bool:
    value = _query_value(request, "dbs") or _query_value(request, "detail")
    return str(value or "").strip().lower() in {"all", "full", "verbose"}


def _iter_db_entries(candidate: Any) -> list[tuple[str, Any]]:
    if candidate is None:
        return []
    if _has_execute(candidate):
        return [("default", candidate)]
    if isinstance(candidate, Mapping):
        return [
            (str(name), db)
            for name, db in candidate.items()
            if _has_execute(db)
        ]
    if isinstance(candidate, Iterable) and not isinstance(
        candidate, (str, bytes, bytearray)
    ):
        return [
            (str(index), db)
            for index, db in enumerate(candidate)
            if _has_execute(db)
        ]
    return []


def _resolve_db_entries(candidate: Any, *sources: Any) -> list[tuple[str, Any]]:
    entries = _iter_db_entries(candidate)
    if entries:
        return entries

    state = getattr(candidate, "state", None)
    app = getattr(candidate, "app", None)
    for source in (state, app, *sources):
        if source is None:
            continue
        for attr in ("dbs", "databases", "engines", "db"):
            entries = _iter_db_entries(getattr(source, attr, None))
            if entries:
                return entries
    return []


async def _check_db(name: str, db: Any) -> dict[str, Any]:
    try:
        await maybe_execute(db, "SELECT 1")
        return {"name": name, "ok": True}
    except Exception as exc:  # pragma: no cover - covered by fixture fakes
        logger.warning("/healthz degraded for %s: %s", name, exc)
        return {
            "name": name,
            "ok": False,
            "warning": _UNAVAILABLE_WARNING,
            "error": str(exc),
        }


def _multi_db_payload(results: list[dict[str, Any]], *, include_all: bool) -> dict[str, Any]:
    total = len(results)
    healthy = sum(1 for item in results if item["ok"])
    payload: dict[str, Any] = {
        "ok": healthy == total,
        "dbs": {
            "ok": healthy,
            "total": total,
            "failed": total - healthy,
        },
    }
    if healthy != total:
        payload["warning"] = _UNAVAILABLE_WARNING
    if include_all:
        payload["databases"] = results
    return payload


def build_healthz_endpoint(
    dep: Optional[Callable[..., Any]],
    *,
    router: Any | None = None,
    warn_no_db: bool = False,
):
    """
    Returns a ASGI endpoint function for /healthz.
    If `dep` is provided, it's used as a dependency to supply `db`.
    Otherwise, we try request.state.db.
    """
    if dep is not None:

        async def _healthz(db: Any = Depends(dep)):
            if hasattr(db, "dependency") and callable(getattr(db, "dependency", None)):
                resolved = db.dependency()
                if inspect.isawaitable(resolved):
                    resolved = await resolved
                db = resolved
            entries = _resolve_db_entries(db, router)
            if not entries:
                if warn_no_db:
                    return {"ok": True, "warning": _NO_DB_WARNING}
                return {"ok": True}
            if len(entries) == 1:
                result = await _check_db(*entries[0])
                if result["ok"]:
                    return {"ok": True}
                return JSONResponse(
                    {
                        "ok": False,
                        "warning": result["warning"],
                        "error": result["error"],
                    },
                    status_code=200,
                )
            results = [await _check_db(name, db) for name, db in entries]
            return _multi_db_payload(results, include_all=False)

        return _healthz

    async def _healthz(request: Request):
        entries = _resolve_db_entries(request, router)
        if not entries:
            if warn_no_db or _query_flag(request, "warn_no_db"):
                return {"ok": True, "warning": _NO_DB_WARNING}
            return {"ok": True}
        if len(entries) == 1:
            result = await _check_db(*entries[0])
            if result["ok"]:
                return {"ok": True}
            return JSONResponse(
                {
                    "ok": False,
                    "warning": result["warning"],
                    "error": result["error"],
                },
                status_code=200,
            )
        results = [await _check_db(name, db) for name, db in entries]
        return _multi_db_payload(results, include_all=_wants_all_dbs(request))

    return _healthz


def _with_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def build_healthz_html(router: Any, request: Any, *, healthz_path: str | None = None) -> str:
    """Return a small operator-facing HTML page for the JSON health endpoint."""

    base = (getattr(request, "script_name", "") or "").rstrip("/")
    configured = healthz_path or f"{getattr(router, 'system_prefix', '/system')}/healthz"
    payload_url = f"{base}{_with_leading_slash(configured)}"
    title = getattr(router, "title", "API")
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} health</title>
    <style>
      body {{
        margin: 0;
        min-height: 100vh;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: #111827;
        background: #f8fafc;
      }}
      main {{
        width: min(720px, calc(100% - 32px));
        margin: 0 auto;
        padding: 48px 0;
      }}
      h1 {{
        font-size: 24px;
        font-weight: 650;
        margin: 0 0 16px;
      }}
      pre {{
        overflow: auto;
        padding: 16px;
        background: #111827;
        color: #e5e7eb;
        border-radius: 6px;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Health</h1>
      <pre id="payload">Loading {payload_url}</pre>
    </main>
    <script>
      const payload = document.getElementById("payload");
      fetch("{payload_url}", {{ headers: {{ "accept": "application/json" }} }})
        .then((response) => response.json())
        .then((data) => {{
          payload.textContent = JSON.stringify(data, null, 2);
          payload.dataset.ok = String(data.ok === true);
        }})
        .catch((error) => {{
          payload.textContent = JSON.stringify({{ ok: false, error: String(error) }}, null, 2);
          payload.dataset.ok = "false";
        }});
    </script>
  </body>
</html>
"""


def mount_healthz_uix(
    router: Any,
    *,
    path: str = "/healthz",
    name: str = "__healthz_uix__",
    healthz_path: str | None = None,
) -> Any:
    """Mount a human-viewable health page that reads the JSON health endpoint."""

    def _healthz_uix_handler(request: Any) -> Response:
        return Response.html(
            build_healthz_html(router, request, healthz_path=healthz_path)
        )

    router.add_route(
        path,
        _healthz_uix_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
        inherit_owner_dependencies=False,
    )
    return router
