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
