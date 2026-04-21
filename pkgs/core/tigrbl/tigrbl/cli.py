"""Unified ``tigrbl`` command-line interface."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import importlib.util
import inspect
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from . import TigrblApp, TigrblRouter
from .engine import known_engine_kinds, load_engine_plugins
from .system import mount_lens, mount_openapi, mount_openrpc, mount_swagger
from tigrbl_core._spec.engine_spec import EngineSpec

SUPPORTED_SERVERS = ("tigrcorn", "uvicorn", "hypercorn", "gunicorn")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_DOCS_PATH = "/docs"
DEFAULT_OPENAPI_PATH = "/openapi.json"
DEFAULT_OPENRPC_PATH = "/openrpc.json"
DEFAULT_LENS_PATH = "/lens"
COMMAND_NAMES = (
    "run",
    "serve",
    "dev",
    "routes",
    "openapi",
    "openrpc",
    "doctor",
    "capabilities",
)
CLI_FLAG_NAMES = (
    "--server",
    "--host",
    "--port",
    "--reload",
    "--workers",
    "--root-path",
    "--proxy-headers",
    "--uds",
    "--docs-path",
    "--openapi-path",
    "--openrpc-path",
    "--lens-path",
    "--statsd-addr",
    "--dogstatsd-tags",
    "--otel-endpoint",
    "--trace-sample-rate",
    "--drain-timeout",
    "--shutdown-timeout",
    "--concurrency-limit",
    "--admission-queue",
    "--backlog",
    "--ws-heartbeat",
    "--ws-heartbeat-timeout",
    "--http2-max-concurrent-streams",
    "--http2-initial-window-size",
    "--http3-max-data",
    "--http3-max-uni-streams",
    "--alpn-policy",
    "--ocsp-policy",
    "--revocation-policy",
    "--interop-bundle-dir",
    "--benchmark-bundle-dir",
    "--deployment-profile",
    "--proxy-contract",
    "--early-data-policy",
    "--origin-static-policy",
    "--quic-metrics",
    "--qlog-dir",
)


class CLIError(RuntimeError):
    """User-facing CLI validation error."""


@dataclass(slots=True)
class ServeConfig:
    server: str = "uvicorn"
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    reload: bool = False
    workers: int = 1
    root_path: str = ""
    proxy_headers: bool = False
    uds: str | None = None
    docs_path: str = DEFAULT_DOCS_PATH
    openapi_path: str = DEFAULT_OPENAPI_PATH
    openrpc_path: str = DEFAULT_OPENRPC_PATH
    lens_path: str = DEFAULT_LENS_PATH
    statsd_addr: str | None = None
    dogstatsd_tags: tuple[str, ...] = ()
    otel_endpoint: str | None = None
    trace_sample_rate: float = 1.0
    drain_timeout: float = 30.0
    shutdown_timeout: float = 30.0
    concurrency_limit: int | None = None
    admission_queue: int = 1024
    backlog: int = 2048
    ws_heartbeat: float = 30.0
    ws_heartbeat_timeout: float = 30.0
    http2_max_concurrent_streams: int = 128
    http2_initial_window_size: int = 65535
    http3_max_data: int = 1048576
    http3_max_uni_streams: int = 128
    alpn_policy: tuple[str, ...] = ("h3", "h2", "http/1.1")
    ocsp_policy: str = "optional"
    revocation_policy: str = "best_effort"
    interop_bundle_dir: str | None = None
    benchmark_bundle_dir: str | None = None
    deployment_profile: str | None = None
    proxy_contract: str = "strict"
    early_data_policy: str = "reject"
    origin_static_policy: str = "strict"
    quic_metrics: tuple[str, ...] = ("connections", "handshake", "retry", "migration")
    qlog_dir: str | None = None


class _RootPathWrapper:
    def __init__(self, app: Any, root_path: str) -> None:
        self._app = app
        self._root_path = root_path

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> Any:
        mutable_scope = dict(scope)
        if self._root_path:
            mutable_scope["root_path"] = self._root_path
        return await self._app(mutable_scope, receive, send)


@dataclass(slots=True)
class _GunicornApplication:
    app: Any
    options: dict[str, Any]

    def run(self) -> Any:
        try:
            from gunicorn.app.base import BaseApplication
        except ImportError as exc:  # pragma: no cover - import exercised in tests via monkeypatch
            raise CLIError(
                "Gunicorn support requires the 'gunicorn' package to be installed."
            ) from exc

        app = self.app
        options = dict(self.options)

        class _Application(BaseApplication):
            def __init__(self) -> None:
                self._app = app
                self._options = options
                super().__init__()

            def load_config(self) -> None:
                for key, value in self._options.items():
                    if value is None:
                        continue
                    if key in self.cfg.settings:
                        self.cfg.set(key, value)

            def load(self) -> Any:
                return self._app

        return _Application().run()


def _normalize_path(path: str, default: str) -> str:
    raw = (path or default).strip() or default
    return raw if raw.startswith("/") else f"/{raw}"


def _csv_tuple(value: str | None) -> tuple[str, ...]:
    if value is None:
        return ()
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


def _resolve_target(args: argparse.Namespace) -> str | None:
    target = getattr(args, "target", None)
    app_flag = getattr(args, "app", None)
    if target and app_flag and target != app_flag:
        raise CLIError("target and --app must reference the same object when both are provided")
    return app_flag or target


def _load_module_from_path(path: Path) -> Any:
    module_name = f"_tigrbl_cli_{path.stem}_{abs(hash(str(path.resolve())))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise CLIError(f"Could not load Python module from '{path}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_target_object(target: str) -> Any:
    raw = (target or "").strip()
    if not raw:
        raise CLIError("An app target is required. Use <module:attr> or <path.py:attr>.")

    source, attr = (raw.split(":", 1) + ["app"])[:2] if ":" in raw else (raw, "app")
    source_path = Path(source)
    if source.endswith(".py") or source_path.exists():
        if not source_path.exists():
            raise CLIError(f"App file '{source}' does not exist")
        module = _load_module_from_path(source_path)
    else:
        module = importlib.import_module(source)

    if not hasattr(module, attr):
        raise CLIError(f"Target '{raw}' could not resolve attribute '{attr}'")
    return getattr(module, attr)


def _coerce_target_to_app(obj: Any) -> Any:
    candidate = obj
    if inspect.isclass(candidate):
        candidate = candidate()
    elif callable(candidate) and not hasattr(candidate, "routes"):
        try:
            created = candidate()
        except TypeError:
            created = candidate
        candidate = created

    routed = getattr(candidate, "router", None)
    if routed is not None and hasattr(routed, "routes") and hasattr(routed, "websocket_routes"):
        candidate = routed

    if isinstance(candidate, TigrblApp):
        return candidate

    if isinstance(candidate, TigrblRouter) or (
        hasattr(candidate, "routes") and hasattr(candidate, "websocket_routes") and type(candidate).__name__.lower().endswith("router")
    ):
        wrapper = TigrblApp(
            title=getattr(candidate, "title", "Tigrbl CLI App"),
            version=getattr(candidate, "version", "0.1.0"),
            mount_system=False,
            engine=getattr(candidate, "engine", None),
        )
        wrapper.include_router(candidate)
        return wrapper

    if callable(candidate) and hasattr(candidate, "routes"):
        return candidate

    raise CLIError(
        "Resolved target is not a Tigrbl app/router or zero-argument app factory."
    )


def _maybe_initialize(app: Any) -> None:
    if getattr(app, "_tigrbl_cli_initialized", False):
        return
    initialize = getattr(app, "initialize", None)
    if not callable(initialize):
        return
    result = initialize()
    if inspect.isawaitable(result):
        asyncio.run(result)
    setattr(app, "_tigrbl_cli_initialized", True)


def _route_exists(app: Any, path: str) -> bool:
    normalized = path.rstrip("/") or "/"
    for route in list(getattr(app, "routes", []) or []):
        route_path = str(getattr(route, "path", "") or "").rstrip("/") or "/"
        if route_path == normalized:
            return True
    return False


def _ensure_docs_mounts(app: Any, cfg: ServeConfig) -> None:
    cfg.openapi_path = _normalize_path(cfg.openapi_path, DEFAULT_OPENAPI_PATH)
    cfg.docs_path = _normalize_path(cfg.docs_path, DEFAULT_DOCS_PATH)
    cfg.openrpc_path = _normalize_path(cfg.openrpc_path, DEFAULT_OPENRPC_PATH)
    cfg.lens_path = _normalize_path(cfg.lens_path, DEFAULT_LENS_PATH)

    if hasattr(app, "openapi_url"):
        setattr(app, "openapi_url", cfg.openapi_path)
    if hasattr(app, "docs_url"):
        setattr(app, "docs_url", cfg.docs_path)
    setattr(app, "openrpc_path", cfg.openrpc_path)

    if not _route_exists(app, cfg.openapi_path):
        mount_openapi(app, path=cfg.openapi_path)
    if not _route_exists(app, cfg.docs_path):
        mount_swagger(app, path=cfg.docs_path)
    if not _route_exists(app, cfg.openrpc_path):
        mount_openrpc(app, path=cfg.openrpc_path)
    if not _route_exists(app, cfg.lens_path):
        mount_lens(app, path=cfg.lens_path, spec_path=cfg.openrpc_path)


def _wrap_app_for_root_path(app: Any, root_path: str) -> Any:
    normalized_root = (root_path or "").strip()
    if not normalized_root:
        return app
    return _RootPathWrapper(app, normalized_root)


def _server_available(name: str) -> bool:
    if name == "tigrcorn":
        return importlib.util.find_spec("tigrcorn") is not None or shutil.which("tigrcorn") is not None
    if name == "gunicorn":
        return importlib.util.find_spec("gunicorn") is not None or shutil.which("gunicorn") is not None
    return importlib.util.find_spec(name) is not None


def _installed_servers() -> dict[str, bool]:
    return {name: _server_available(name) for name in SUPPORTED_SERVERS}


def _engine_supports(app: Any) -> dict[str, Any] | None:
    engine_obj = getattr(app, "engine", None)
    if engine_obj is None:
        return None
    try:
        spec = EngineSpec.from_any(engine_obj)
    except Exception:
        return None
    if spec is None:
        return None
    try:
        return dict(spec.supports())
    except Exception:
        return None


def _summarize_routes(app: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for route in list(getattr(app, "routes", []) or []):
        methods = ",".join(sorted(tuple(getattr(route, "methods", ()) or ())))
        rows.append(
            {
                "kind": "http",
                "methods": methods,
                "path": str(getattr(route, "path", getattr(route, "path_template", "")) or ""),
                "name": str(getattr(route, "name", "") or ""),
            }
        )
    for route in list(getattr(app, "websocket_routes", []) or []):
        rows.append(
            {
                "kind": "websocket",
                "methods": "WS",
                "path": str(getattr(route, "path_template", "") or ""),
                "name": str(getattr(route, "name", "") or ""),
            }
        )
    for mount in list(getattr(app, "_static_mounts", []) or []):
        rows.append(
            {
                "kind": "static",
                "methods": "GET",
                "path": f"{mount.get('path', '/static').rstrip('/') or '/'}/*",
                "name": "static",
            }
        )
    return sorted(rows, key=lambda row: (row["path"], row["methods"], row["name"]))


def _render_route_table(rows: Iterable[dict[str, str]]) -> str:
    items = list(rows)
    if not items:
        return "KIND      METHODS  PATH  NAME\n"
    widths = {
        "kind": max(len("KIND"), max(len(item["kind"]) for item in items)),
        "methods": max(len("METHODS"), max(len(item["methods"]) for item in items)),
        "path": max(len("PATH"), max(len(item["path"]) for item in items)),
        "name": max(len("NAME"), max(len(item["name"]) for item in items)),
    }
    header = (
        f"{'KIND'.ljust(widths['kind'])}  "
        f"{'METHODS'.ljust(widths['methods'])}  "
        f"{'PATH'.ljust(widths['path'])}  "
        f"{'NAME'.ljust(widths['name'])}"
    )
    body = [header]
    for item in items:
        body.append(
            f"{item['kind'].ljust(widths['kind'])}  "
            f"{item['methods'].ljust(widths['methods'])}  "
            f"{item['path'].ljust(widths['path'])}  "
            f"{item['name'].ljust(widths['name'])}"
        )
    return "\n".join(body) + "\n"


def _json_text(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _build_doctor_payload(app: Any, cfg: ServeConfig, target: str) -> dict[str, Any]:
    routes = _summarize_routes(app)
    return {
        "target": target,
        "app_type": type(app).__name__,
        "title": getattr(app, "title", "API"),
        "version": getattr(app, "version", "0.1.0"),
        "routes": {
            "count": len([item for item in routes if item["kind"] == "http"]),
            "websocket_count": len([item for item in routes if item["kind"] == "websocket"]),
            "static_mount_count": len([item for item in routes if item["kind"] == "static"]),
        },
        "docs_paths": {
            "docs": cfg.docs_path,
            "openapi": cfg.openapi_path,
            "openrpc": cfg.openrpc_path,
            "lens": cfg.lens_path,
        },
        "engine_capabilities": _engine_supports(app),
        "supported_servers": _installed_servers(),
        "known_engine_kinds": list(known_engine_kinds()),
        "operator_controls": {
            "statsd_addr": cfg.statsd_addr,
            "dogstatsd_tags": list(cfg.dogstatsd_tags),
            "otel_endpoint": cfg.otel_endpoint,
            "trace_sample_rate": cfg.trace_sample_rate,
            "drain_timeout": cfg.drain_timeout,
            "shutdown_timeout": cfg.shutdown_timeout,
            "concurrency_limit": cfg.concurrency_limit,
            "admission_queue": cfg.admission_queue,
            "backlog": cfg.backlog,
            "ws_heartbeat": cfg.ws_heartbeat,
            "ws_heartbeat_timeout": cfg.ws_heartbeat_timeout,
            "http2_max_concurrent_streams": cfg.http2_max_concurrent_streams,
            "http2_initial_window_size": cfg.http2_initial_window_size,
            "http3_max_data": cfg.http3_max_data,
            "http3_max_uni_streams": cfg.http3_max_uni_streams,
            "alpn_policy": list(cfg.alpn_policy),
            "ocsp_policy": cfg.ocsp_policy,
            "revocation_policy": cfg.revocation_policy,
            "interop_bundle_dir": cfg.interop_bundle_dir,
            "benchmark_bundle_dir": cfg.benchmark_bundle_dir,
            "deployment_profile": cfg.deployment_profile,
            "proxy_contract": cfg.proxy_contract,
            "early_data_policy": cfg.early_data_policy,
            "origin_static_policy": cfg.origin_static_policy,
            "quic_metrics": list(cfg.quic_metrics),
            "qlog_dir": cfg.qlog_dir,
        },
    }


def _load_prepared_app(target: str, cfg: ServeConfig | None = None) -> Any:
    raw = _load_target_object(target)
    app = _coerce_target_to_app(raw)
    _maybe_initialize(app)
    if cfg is not None:
        _ensure_docs_mounts(app, cfg)
    return app


def _run_with_uvicorn(app: Any, cfg: ServeConfig) -> int:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise CLIError("Uvicorn support requires the 'uvicorn' package to be installed.") from exc
    uvicorn.run(
        app,
        host=cfg.host,
        port=cfg.port,
        reload=cfg.reload,
        workers=cfg.workers,
        root_path=cfg.root_path,
        proxy_headers=cfg.proxy_headers,
        uds=cfg.uds,
    )
    return 0


def _run_with_hypercorn(app: Any, cfg: ServeConfig) -> int:
    try:
        from hypercorn.asyncio import serve as hypercorn_serve
        from hypercorn.config import Config
    except ImportError as exc:  # pragma: no cover
        raise CLIError("Hypercorn support requires the 'hypercorn' package to be installed.") from exc

    config = Config()
    if cfg.uds:
        config.bind = [f"unix:{cfg.uds}"]
    else:
        config.bind = [f"{cfg.host}:{cfg.port}"]
    config.use_reloader = bool(cfg.reload)
    config.workers = int(cfg.workers)
    if hasattr(config, "root_path"):
        config.root_path = cfg.root_path
    if hasattr(config, "proxy_mode") and cfg.proxy_headers:
        config.proxy_mode = "legacy"
    asyncio.run(hypercorn_serve(app, config))
    return 0


def _run_with_gunicorn(app: Any, cfg: ServeConfig) -> int:
    options = {
        "bind": f"unix:{cfg.uds}" if cfg.uds else f"{cfg.host}:{cfg.port}",
        "workers": int(cfg.workers),
        "reload": bool(cfg.reload),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "forwarded_allow_ips": "*" if cfg.proxy_headers else None,
    }
    _GunicornApplication(app, options).run()
    return 0


def _run_with_tigrcorn(app: Any, cfg: ServeConfig) -> int:
    try:
        module = importlib.import_module("tigrcorn")
    except ImportError as exc:  # pragma: no cover
        raise CLIError("Tigrcorn support requires the 'tigrcorn' package to be installed.") from exc

    for attr in ("run", "serve"):
        fn = getattr(module, attr, None)
        if callable(fn):
            fn(
                app,
                host=cfg.host,
                port=cfg.port,
                reload=cfg.reload,
                workers=cfg.workers,
                root_path=cfg.root_path,
                proxy_headers=cfg.proxy_headers,
                uds=cfg.uds,
                statsd_addr=cfg.statsd_addr,
                dogstatsd_tags=list(cfg.dogstatsd_tags),
                otel_endpoint=cfg.otel_endpoint,
                trace_sample_rate=cfg.trace_sample_rate,
                drain_timeout=cfg.drain_timeout,
                shutdown_timeout=cfg.shutdown_timeout,
                concurrency_limit=cfg.concurrency_limit,
                admission_queue=cfg.admission_queue,
                backlog=cfg.backlog,
                ws_heartbeat=cfg.ws_heartbeat,
                ws_heartbeat_timeout=cfg.ws_heartbeat_timeout,
                http2_max_concurrent_streams=cfg.http2_max_concurrent_streams,
                http2_initial_window_size=cfg.http2_initial_window_size,
                http3_max_data=cfg.http3_max_data,
                http3_max_uni_streams=cfg.http3_max_uni_streams,
                alpn_policy=list(cfg.alpn_policy),
                ocsp_policy=cfg.ocsp_policy,
                revocation_policy=cfg.revocation_policy,
                interop_bundle_dir=cfg.interop_bundle_dir,
                benchmark_bundle_dir=cfg.benchmark_bundle_dir,
                deployment_profile=cfg.deployment_profile,
                proxy_contract=cfg.proxy_contract,
                early_data_policy=cfg.early_data_policy,
                origin_static_policy=cfg.origin_static_policy,
                quic_metrics=list(cfg.quic_metrics),
                qlog_dir=cfg.qlog_dir,
            )
            return 0
    raise CLIError("The installed 'tigrcorn' module does not expose a compatible run/serve callable.")


SERVER_RUNNERS: dict[str, Callable[[Any, ServeConfig], int]] = {
    "uvicorn": _run_with_uvicorn,
    "hypercorn": _run_with_hypercorn,
    "gunicorn": _run_with_gunicorn,
    "tigrcorn": _run_with_tigrcorn,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tigrbl", description="Unified Tigrbl CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_target(sp: argparse.ArgumentParser, *, required: bool = True) -> None:
        nargs = None if required else "?"
        sp.add_argument("target", nargs=nargs, help="App target as <module:attr> or <path.py:attr>")
        sp.add_argument("--app", dest="app", help="Explicit app target as <module:attr> or <path.py:attr>")

    def add_docs_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--docs-path", default=DEFAULT_DOCS_PATH)
        sp.add_argument("--openapi-path", default=DEFAULT_OPENAPI_PATH)
        sp.add_argument("--openrpc-path", default=DEFAULT_OPENRPC_PATH)
        sp.add_argument("--lens-path", default=DEFAULT_LENS_PATH)

    def add_server_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--server", choices=SUPPORTED_SERVERS, default="uvicorn")
        sp.add_argument("--host", default=DEFAULT_HOST)
        sp.add_argument("--port", type=int, default=DEFAULT_PORT)
        sp.add_argument("--reload", action="store_true")
        sp.add_argument("--workers", type=int, default=1)
        sp.add_argument("--root-path", default="")
        sp.add_argument("--proxy-headers", action="store_true")
        sp.add_argument("--uds")
        sp.add_argument("--statsd-addr")
        sp.add_argument("--dogstatsd-tags", default="")
        sp.add_argument("--otel-endpoint")
        sp.add_argument("--trace-sample-rate", type=float, default=1.0)
        sp.add_argument("--drain-timeout", type=float, default=30.0)
        sp.add_argument("--shutdown-timeout", type=float, default=30.0)
        sp.add_argument("--concurrency-limit", type=int)
        sp.add_argument("--admission-queue", type=int, default=1024)
        sp.add_argument("--backlog", type=int, default=2048)
        sp.add_argument("--ws-heartbeat", type=float, default=30.0)
        sp.add_argument("--ws-heartbeat-timeout", type=float, default=30.0)
        sp.add_argument("--http2-max-concurrent-streams", type=int, default=128)
        sp.add_argument("--http2-initial-window-size", type=int, default=65535)
        sp.add_argument("--http3-max-data", type=int, default=1048576)
        sp.add_argument("--http3-max-uni-streams", type=int, default=128)
        sp.add_argument("--alpn-policy", default="h3,h2,http/1.1")
        sp.add_argument("--ocsp-policy", choices=("disabled", "optional", "strict"), default="optional")
        sp.add_argument(
            "--revocation-policy",
            choices=("disabled", "best_effort", "strict"),
            default="best_effort",
        )
        sp.add_argument("--interop-bundle-dir")
        sp.add_argument("--benchmark-bundle-dir")
        sp.add_argument(
            "--deployment-profile",
            choices=(
                "strict-h1-origin",
                "strict-h2-origin",
                "strict-h3-edge",
                "strict-mtls-origin",
                "static-origin",
            ),
        )
        sp.add_argument(
            "--proxy-contract",
            choices=("strict", "trusted-proxy", "edge-normalized"),
            default="strict",
        )
        sp.add_argument(
            "--early-data-policy",
            choices=("reject", "idempotent-only", "edge-replay-guarded"),
            default="reject",
        )
        sp.add_argument(
            "--origin-static-policy",
            choices=("strict", "static-origin", "edge-static"),
            default="strict",
        )
        sp.add_argument(
            "--quic-metrics",
            default="connections,handshake,retry,migration",
            help="Comma-separated stable QUIC counters to emit; qlog remains experimental via --qlog-dir.",
        )
        sp.add_argument("--qlog-dir")
        add_docs_flags(sp)

    for name in ("run", "serve", "dev"):
        sp = subparsers.add_parser(name, help=f"{name.title()} a Tigrbl app")
        add_target(sp, required=True)
        add_server_flags(sp)

    for name in ("routes", "openapi", "openrpc"):
        sp = subparsers.add_parser(name, help=f"Inspect a Tigrbl app via {name}")
        add_target(sp, required=True)
        add_docs_flags(sp)

    sp = subparsers.add_parser("doctor", help="Inspect a Tigrbl app via doctor")
    add_target(sp, required=True)
    add_server_flags(sp)

    sp = subparsers.add_parser("capabilities", help="Show CLI/server/engine capabilities")
    add_target(sp, required=False)
    add_server_flags(sp)

    return parser


def _serve_config_from_args(args: argparse.Namespace) -> ServeConfig:
    cfg = ServeConfig(
        server=getattr(args, "server", "uvicorn"),
        host=getattr(args, "host", DEFAULT_HOST),
        port=int(getattr(args, "port", DEFAULT_PORT)),
        reload=bool(getattr(args, "reload", False)),
        workers=int(getattr(args, "workers", 1)),
        root_path=str(getattr(args, "root_path", "") or ""),
        proxy_headers=bool(getattr(args, "proxy_headers", False)),
        uds=getattr(args, "uds", None),
        docs_path=str(getattr(args, "docs_path", DEFAULT_DOCS_PATH) or DEFAULT_DOCS_PATH),
        openapi_path=str(getattr(args, "openapi_path", DEFAULT_OPENAPI_PATH) or DEFAULT_OPENAPI_PATH),
        openrpc_path=str(getattr(args, "openrpc_path", DEFAULT_OPENRPC_PATH) or DEFAULT_OPENRPC_PATH),
        lens_path=str(getattr(args, "lens_path", DEFAULT_LENS_PATH) or DEFAULT_LENS_PATH),
        statsd_addr=getattr(args, "statsd_addr", None),
        dogstatsd_tags=_csv_tuple(getattr(args, "dogstatsd_tags", "")),
        otel_endpoint=getattr(args, "otel_endpoint", None),
        trace_sample_rate=float(getattr(args, "trace_sample_rate", 1.0)),
        drain_timeout=float(getattr(args, "drain_timeout", 30.0)),
        shutdown_timeout=float(getattr(args, "shutdown_timeout", 30.0)),
        concurrency_limit=getattr(args, "concurrency_limit", None),
        admission_queue=int(getattr(args, "admission_queue", 1024)),
        backlog=int(getattr(args, "backlog", 2048)),
        ws_heartbeat=float(getattr(args, "ws_heartbeat", 30.0)),
        ws_heartbeat_timeout=float(getattr(args, "ws_heartbeat_timeout", 30.0)),
        http2_max_concurrent_streams=int(getattr(args, "http2_max_concurrent_streams", 128)),
        http2_initial_window_size=int(getattr(args, "http2_initial_window_size", 65535)),
        http3_max_data=int(getattr(args, "http3_max_data", 1048576)),
        http3_max_uni_streams=int(getattr(args, "http3_max_uni_streams", 128)),
        alpn_policy=_csv_tuple(getattr(args, "alpn_policy", "h3,h2,http/1.1")),
        ocsp_policy=str(getattr(args, "ocsp_policy", "optional")),
        revocation_policy=str(getattr(args, "revocation_policy", "best_effort")),
        interop_bundle_dir=getattr(args, "interop_bundle_dir", None),
        benchmark_bundle_dir=getattr(args, "benchmark_bundle_dir", None),
        deployment_profile=getattr(args, "deployment_profile", None),
        proxy_contract=str(getattr(args, "proxy_contract", "strict")),
        early_data_policy=str(getattr(args, "early_data_policy", "reject")),
        origin_static_policy=str(getattr(args, "origin_static_policy", "strict")),
        quic_metrics=_csv_tuple(getattr(args, "quic_metrics", "connections,handshake,retry,migration")),
        qlog_dir=getattr(args, "qlog_dir", None),
    )
    if cfg.workers < 1:
        raise CLIError("--workers must be >= 1")
    if cfg.trace_sample_rate < 0.0 or cfg.trace_sample_rate > 1.0:
        raise CLIError("--trace-sample-rate must be between 0.0 and 1.0")
    if cfg.drain_timeout < 0.0:
        raise CLIError("--drain-timeout must be >= 0")
    if cfg.shutdown_timeout < 0.0:
        raise CLIError("--shutdown-timeout must be >= 0")
    if cfg.concurrency_limit is not None and cfg.concurrency_limit < 1:
        raise CLIError("--concurrency-limit must be >= 1")
    if cfg.admission_queue < 1:
        raise CLIError("--admission-queue must be >= 1")
    if cfg.backlog < 1:
        raise CLIError("--backlog must be >= 1")
    if cfg.ws_heartbeat < 0.0:
        raise CLIError("--ws-heartbeat must be >= 0")
    if cfg.ws_heartbeat_timeout < 0.0:
        raise CLIError("--ws-heartbeat-timeout must be >= 0")
    if cfg.http2_max_concurrent_streams < 1:
        raise CLIError("--http2-max-concurrent-streams must be >= 1")
    if cfg.http2_initial_window_size < 1:
        raise CLIError("--http2-initial-window-size must be >= 1")
    if cfg.http3_max_data < 1:
        raise CLIError("--http3-max-data must be >= 1")
    if cfg.http3_max_uni_streams < 1:
        raise CLIError("--http3-max-uni-streams must be >= 1")
    if not cfg.alpn_policy:
        raise CLIError("--alpn-policy must include at least one protocol")
    if not cfg.quic_metrics:
        raise CLIError("--quic-metrics must include at least one counter")
    return cfg


def _handle_run_like(command: str, args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    if target is None:
        raise CLIError("An app target is required for serve/run/dev")
    cfg = _serve_config_from_args(args)
    if command == "dev" and not getattr(args, "reload", False):
        cfg.reload = True
    app = _load_prepared_app(target, cfg)
    wrapped_app = _wrap_app_for_root_path(app, cfg.root_path)
    runner = SERVER_RUNNERS[cfg.server]
    return runner(wrapped_app, cfg)


def _handle_routes(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    if target is None:
        raise CLIError("An app target is required for routes")
    cfg = _serve_config_from_args(args)
    app = _load_prepared_app(target, cfg)
    sys.stdout.write(_render_route_table(_summarize_routes(app)))
    return 0


def _handle_openapi(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    if target is None:
        raise CLIError("An app target is required for openapi")
    cfg = _serve_config_from_args(args)
    app = _load_prepared_app(target, cfg)
    build = getattr(app, "openapi", None)
    if callable(build):
        payload = build()
    else:
        from .system import build_openapi

        payload = build_openapi(app)
    sys.stdout.write(_json_text(payload))
    return 0


def _handle_openrpc(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    if target is None:
        raise CLIError("An app target is required for openrpc")
    cfg = _serve_config_from_args(args)
    app = _load_prepared_app(target, cfg)
    build = getattr(app, "openrpc", None)
    if callable(build):
        payload = build()
    else:
        from .system import build_openrpc_spec

        payload = build_openrpc_spec(app)
    sys.stdout.write(_json_text(payload))
    return 0


def _handle_doctor(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    if target is None:
        raise CLIError("An app target is required for doctor")
    cfg = _serve_config_from_args(args)
    app = _load_prepared_app(target, cfg)
    sys.stdout.write(_json_text(_build_doctor_payload(app, cfg, target)))
    return 0


def _handle_capabilities(args: argparse.Namespace) -> int:
    load_engine_plugins()
    payload: dict[str, Any] = {
        "commands": list(COMMAND_NAMES),
        "flags": list(CLI_FLAG_NAMES),
        "servers": _installed_servers(),
        "known_engine_kinds": list(known_engine_kinds()),
    }
    target = _resolve_target(args)
    if target:
        cfg = _serve_config_from_args(args)
        app = _load_prepared_app(target, cfg)
        payload["app"] = _build_doctor_payload(app, cfg, target)
    sys.stdout.write(_json_text(payload))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        match args.command:
            case "run" | "serve" | "dev":
                return _handle_run_like(args.command, args)
            case "routes":
                return _handle_routes(args)
            case "openapi":
                return _handle_openapi(args)
            case "openrpc":
                return _handle_openrpc(args)
            case "doctor":
                return _handle_doctor(args)
            case "capabilities":
                return _handle_capabilities(args)
    except CLIError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


def console_main() -> None:
    raise SystemExit(main())


if __name__ == "__main__":  # pragma: no cover
    console_main()
