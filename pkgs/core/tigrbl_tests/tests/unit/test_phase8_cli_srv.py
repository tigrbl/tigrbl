from __future__ import annotations

import types
from pathlib import Path

import pytest

from tigrbl import cli as tigrbl_cli


REPO_ROOT = Path(__file__).resolve().parents[5]
FIXTURE = REPO_ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "fixtures" / "phase8_cli_app.py"
TARGET = f"{FIXTURE}:app"


def _cfg(**overrides):
    base = tigrbl_cli.ServeConfig(
        server="uvicorn",
        host="0.0.0.0",
        port=9001,
        reload=False,
        workers=2,
        root_path="/root",
        proxy_headers=True,
        uds="/tmp/tigrbl.sock",
        docs_path="/api-docs",
        openapi_path="/schema.json",
        openrpc_path="/rpc.json",
        lens_path="/rpc-ui",
        statsd_addr="127.0.0.1:8125",
        dogstatsd_tags=("env:test", "service:tigrbl"),
        otel_endpoint="http://127.0.0.1:4318",
        trace_sample_rate=0.25,
        drain_timeout=15.0,
        shutdown_timeout=20.0,
        concurrency_limit=64,
        admission_queue=256,
        backlog=512,
        ws_heartbeat=10.0,
        ws_heartbeat_timeout=12.5,
        http2_max_concurrent_streams=96,
        http2_initial_window_size=98304,
        http3_max_data=2097152,
        http3_max_uni_streams=48,
        alpn_policy=("h3", "h2"),
        ocsp_policy="strict",
        revocation_policy="strict",
        interop_bundle_dir="artifacts/interop",
        benchmark_bundle_dir="artifacts/benchmarks",
        deployment_profile="strict-h3-edge",
        proxy_contract="edge-normalized",
        early_data_policy="edge-replay-guarded",
        origin_static_policy="edge-static",
        quic_metrics=("connections", "retry"),
        qlog_dir="artifacts/qlog",
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


@pytest.mark.parametrize("server", ["uvicorn", "hypercorn", "gunicorn", "tigrcorn"])
def test_run_command_dispatches_to_each_supported_server(monkeypatch, server: str) -> None:
    called: dict[str, object] = {}

    def fake_runner(app, cfg):
        called["app"] = app
        called["cfg"] = cfg
        return 0

    monkeypatch.setitem(tigrbl_cli.SERVER_RUNNERS, server, fake_runner)
    rc = tigrbl_cli.main([
        "run",
        TARGET,
        "--server",
        server,
        "--host",
        "0.0.0.0",
        "--port",
        "9001",
        "--workers",
        "2",
        "--root-path",
        "/root",
        "--proxy-headers",
        "--docs-path",
        "/api-docs",
        "--openapi-path",
        "/schema.json",
        "--openrpc-path",
        "/rpc.json",
        "--lens-path",
        "/rpc-ui",
    ])

    assert rc == 0
    cfg = called["cfg"]
    assert cfg.server == server
    assert cfg.host == "0.0.0.0"
    assert cfg.port == 9001
    assert cfg.workers == 2
    assert cfg.root_path == "/root"
    assert cfg.proxy_headers is True
    app = called["app"]
    route_owner = getattr(app, "_app", app)
    routes = {getattr(route, "path", "") for route in getattr(route_owner, "routes", [])}
    assert "/api-docs" in routes
    assert "/schema.json" in routes
    assert "/rpc.json" in routes
    assert "/rpc-ui" in routes


def test_supported_servers_are_locked_to_the_governed_set() -> None:
    assert tigrbl_cli.SUPPORTED_SERVERS == ("tigrcorn", "uvicorn", "hypercorn", "gunicorn")


@pytest.mark.parametrize("server", ["daphne", "twisted", "granian"])
def test_parser_rejects_out_of_boundary_servers(server: str) -> None:
    with pytest.raises(SystemExit):
        tigrbl_cli._build_parser().parse_args(["serve", TARGET, "--server", server])


def test_dev_command_enables_reload_by_default(monkeypatch) -> None:
    called: dict[str, object] = {}

    def fake_runner(_app, cfg):
        called["cfg"] = cfg
        return 0

    monkeypatch.setitem(tigrbl_cli.SERVER_RUNNERS, "uvicorn", fake_runner)
    rc = tigrbl_cli.main(["dev", TARGET])
    assert rc == 0
    assert called["cfg"].reload is True


def test_uvicorn_runner_translates_config(monkeypatch) -> None:
    captured: dict[str, object] = {}
    fake_uvicorn = types.SimpleNamespace(
        run=lambda app, **kwargs: captured.update({"app": app, **kwargs})
    )
    monkeypatch.setitem(__import__("sys").modules, "uvicorn", fake_uvicorn)

    rc = tigrbl_cli._run_with_uvicorn(object(), _cfg(server="uvicorn", uds=None))
    assert rc == 0
    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 9001
    assert captured["root_path"] == "/root"
    assert captured["proxy_headers"] is True


def test_hypercorn_runner_translates_config(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeConfig:
        def __init__(self) -> None:
            self.bind = []
            self.use_reloader = False
            self.workers = 1
            self.root_path = ""
            self.proxy_mode = None

    fake_asyncio_mod = types.ModuleType("hypercorn.asyncio")
    fake_asyncio_mod.serve = lambda app, config: (captured.update({"app": app, "config": config}) or "fake-coro")
    fake_config_mod = types.ModuleType("hypercorn.config")
    fake_config_mod.Config = FakeConfig
    monkeypatch.setitem(__import__("sys").modules, "hypercorn.asyncio", fake_asyncio_mod)
    monkeypatch.setitem(__import__("sys").modules, "hypercorn.config", fake_config_mod)
    monkeypatch.setattr(tigrbl_cli.asyncio, "run", lambda _coro: None)

    rc = tigrbl_cli._run_with_hypercorn(object(), _cfg(server="hypercorn", uds=None))
    assert rc == 0
    config = captured["config"]
    assert config.bind == ["0.0.0.0:9001"]
    assert config.use_reloader is False
    assert config.workers == 2
    assert config.root_path == "/root"
    assert config.proxy_mode == "legacy"


def test_gunicorn_runner_translates_config(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(self):
        captured["options"] = dict(self.options)
        return None

    monkeypatch.setattr(tigrbl_cli._GunicornApplication, "run", fake_run)
    rc = tigrbl_cli._run_with_gunicorn(object(), _cfg(server="gunicorn", uds=None))
    assert rc == 0
    assert captured["options"]["bind"] == "0.0.0.0:9001"
    assert captured["options"]["workers"] == 2
    assert captured["options"]["worker_class"] == "uvicorn.workers.UvicornWorker"
    assert captured["options"]["forwarded_allow_ips"] == "*"


def test_tigrcorn_runner_translates_config(monkeypatch) -> None:
    captured: dict[str, object] = {}
    fake_tigrcorn = types.SimpleNamespace(
        run=lambda app, **kwargs: captured.update({"app": app, **kwargs})
    )
    monkeypatch.setitem(__import__("sys").modules, "tigrcorn", fake_tigrcorn)

    rc = tigrbl_cli._run_with_tigrcorn(object(), _cfg(server="tigrcorn", uds=None))
    assert rc == 0
    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 9001
    assert captured["workers"] == 2
    assert captured["root_path"] == "/root"
    assert captured["proxy_headers"] is True
    assert captured["statsd_addr"] == "127.0.0.1:8125"
    assert captured["dogstatsd_tags"] == ["env:test", "service:tigrbl"]
    assert captured["otel_endpoint"] == "http://127.0.0.1:4318"
    assert captured["trace_sample_rate"] == 0.25
    assert captured["drain_timeout"] == 15.0
    assert captured["shutdown_timeout"] == 20.0
    assert captured["concurrency_limit"] == 64
    assert captured["admission_queue"] == 256
    assert captured["backlog"] == 512
    assert captured["ws_heartbeat"] == 10.0
    assert captured["ws_heartbeat_timeout"] == 12.5
    assert captured["http2_max_concurrent_streams"] == 96
    assert captured["http2_initial_window_size"] == 98304
    assert captured["http3_max_data"] == 2097152
    assert captured["http3_max_uni_streams"] == 48
    assert captured["alpn_policy"] == ["h3", "h2"]
    assert captured["ocsp_policy"] == "strict"
    assert captured["revocation_policy"] == "strict"
    assert captured["interop_bundle_dir"] == "artifacts/interop"
    assert captured["benchmark_bundle_dir"] == "artifacts/benchmarks"
    assert captured["deployment_profile"] == "strict-h3-edge"
    assert captured["proxy_contract"] == "edge-normalized"
    assert captured["early_data_policy"] == "edge-replay-guarded"
    assert captured["origin_static_policy"] == "edge-static"
    assert captured["quic_metrics"] == ["connections", "retry"]
    assert captured["qlog_dir"] == "artifacts/qlog"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["serve", TARGET, "--trace-sample-rate", "1.5"], "--trace-sample-rate must be between 0.0 and 1.0"),
        (["serve", TARGET, "--concurrency-limit", "0"], "--concurrency-limit must be >= 1"),
        (["serve", TARGET, "--admission-queue", "0"], "--admission-queue must be >= 1"),
        (["serve", TARGET, "--backlog", "0"], "--backlog must be >= 1"),
        (["serve", TARGET, "--http2-max-concurrent-streams", "0"], "--http2-max-concurrent-streams must be >= 1"),
        (["serve", TARGET, "--http3-max-data", "0"], "--http3-max-data must be >= 1"),
        (["serve", TARGET, "--alpn-policy", ",,,"], "--alpn-policy must include at least one protocol"),
        (["serve", TARGET, "--quic-metrics", ",,,"], "--quic-metrics must include at least one counter"),
    ],
)
def test_cli_rejects_invalid_tigrcorn_operator_controls(argv: list[str], message: str) -> None:
    with pytest.raises(tigrbl_cli.CLIError, match=message):
        args = tigrbl_cli._build_parser().parse_args(argv)
        tigrbl_cli._serve_config_from_args(args)
