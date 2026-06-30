from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

import pytest

from tigrbl import TigrblApp
from tigrbl import cli as tigrbl_cli


REPO_ROOT = Path(__file__).resolve().parents[5]
FIXTURE = REPO_ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "fixtures" / "cli_smoke_app.py"
FIXTURE_MODULE = "tests.fixtures.cli_smoke_app"


def test_resolve_target_accepts_positional_or_app_flag_and_rejects_mismatch() -> None:
    assert tigrbl_cli._resolve_target(argparse.Namespace(target="pkg:app", app=None)) == "pkg:app"
    assert tigrbl_cli._resolve_target(argparse.Namespace(target=None, app="pkg:app")) == "pkg:app"
    assert tigrbl_cli._resolve_target(argparse.Namespace(target="pkg:app", app="pkg:app")) == "pkg:app"

    with pytest.raises(tigrbl_cli.CLIError, match="target and --app"):
        tigrbl_cli._resolve_target(argparse.Namespace(target="pkg:app", app="other:app"))


def test_module_target_resolution_supports_explicit_attr_and_default_app() -> None:
    explicit = tigrbl_cli._load_target_object(f"{FIXTURE_MODULE}:build_app")
    default = tigrbl_cli._load_target_object(FIXTURE_MODULE)

    assert callable(explicit)
    assert isinstance(default, TigrblApp)
    assert default.title == "CLI Smoke App"


def test_module_target_resolution_raises_clear_error_for_missing_attr() -> None:
    with pytest.raises(tigrbl_cli.CLIError, match="could not resolve attribute 'missing'"):
        tigrbl_cli._load_target_object(f"{FIXTURE_MODULE}:missing")


def test_path_target_resolution_supports_explicit_attr_and_default_app() -> None:
    explicit = tigrbl_cli._load_target_object(f"{FIXTURE}:build_app")
    default = tigrbl_cli._load_target_object(str(FIXTURE))

    assert callable(explicit)
    assert isinstance(default, TigrblApp)
    assert default.title == "CLI Smoke App"


def test_path_target_resolution_uses_stable_module_name() -> None:
    first = tigrbl_cli._load_module_from_path(FIXTURE)
    second = tigrbl_cli._load_module_from_path(FIXTURE)

    assert first.__name__ == second.__name__
    assert first.__name__.startswith("_tigrbl_cli_cli_smoke_app_")


def test_path_target_resolution_raises_clear_error_for_missing_file() -> None:
    missing = FIXTURE.with_name("missing_cli_app.py")

    with pytest.raises(tigrbl_cli.CLIError, match="does not exist"):
        tigrbl_cli._load_target_object(f"{missing}:app")


def test_target_surface_loading_coerces_instances_classes_factories_and_router_wrappers() -> None:
    app = TigrblApp(title="instance", mount_system=False)

    class AppClass(TigrblApp):
        def __init__(self) -> None:
            super().__init__(title="class", mount_system=False)

    def factory() -> TigrblApp:
        return TigrblApp(title="factory", mount_system=False)

    wrapper = SimpleNamespace(router=TigrblApp(title="wrapped", mount_system=False))

    assert tigrbl_cli._coerce_target_to_app(app) is app
    assert tigrbl_cli._coerce_target_to_app(AppClass).title == "class"
    assert tigrbl_cli._coerce_target_to_app(factory).title == "factory"
    assert tigrbl_cli._coerce_target_to_app(wrapper).title == "wrapped"


def test_callable_with_required_args_is_not_invoked_as_zero_arg_factory() -> None:
    def requires_arg(value: object) -> object:
        return value

    with pytest.raises(tigrbl_cli.CLIError, match="zero-argument app factory"):
        tigrbl_cli._coerce_target_to_app(requires_arg)


def test_load_prepared_app_uses_shared_loader_initialization_and_docs_mounts() -> None:
    cfg = tigrbl_cli.ServeConfig(
        server="uvicorn",
        host="127.0.0.1",
        port=8000,
        reload=False,
        workers=1,
        root_path="",
        proxy_headers=False,
        uds=None,
        docs_path="/docs-ui",
        openapi_path="/schema.json",
        openrpc_path="/rpc.json",
        lens_path="/rpc-ui",
    )

    app = tigrbl_cli._load_prepared_app(f"{FIXTURE}:build_app", cfg)
    route_owner = getattr(app, "_app", app)
    routes = {getattr(route, "path", "") for route in getattr(route_owner, "routes", [])}

    assert getattr(app, "_tigrbl_cli_initialized", False) is True
    assert {"/docs-ui", "/schema.json", "/rpc.json", "/rpc-ui"}.issubset(routes)


@pytest.mark.parametrize(
    ("command", "argv"),
    [
        ("run", ["run", f"{FIXTURE}:app"]),
        ("routes", ["routes", f"{FIXTURE}:app"]),
        ("openapi", ["openapi", f"{FIXTURE}:app"]),
        ("openrpc", ["openrpc", f"{FIXTURE}:app"]),
        ("doctor", ["doctor", f"{FIXTURE}:app"]),
        ("capabilities", ["capabilities", f"{FIXTURE}:app"]),
    ],
)
def test_cli_handlers_share_prepared_target_loader(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    argv: list[str],
) -> None:
    calls: list[str] = []
    app = TigrblApp(title="shared", mount_system=False)

    def fake_load(target: str, cfg: tigrbl_cli.ServeConfig | None = None) -> TigrblApp:
        calls.append(target)
        return app

    monkeypatch.setattr(tigrbl_cli, "_load_prepared_app", fake_load)
    monkeypatch.setitem(tigrbl_cli.SERVER_RUNNERS, "uvicorn", lambda _app, _cfg: 0)
    monkeypatch.setattr(tigrbl_cli, "_render_route_table", lambda _summary: "")
    monkeypatch.setattr(tigrbl_cli, "_build_doctor_payload", lambda _app, _cfg, _target: {})
    monkeypatch.setattr(tigrbl_cli, "load_engine_plugins", lambda: None)
    monkeypatch.setattr(tigrbl_cli, "known_engine_kinds", lambda: ())
    monkeypatch.setattr(tigrbl_cli, "_installed_servers", lambda: ("uvicorn",))

    assert tigrbl_cli.main(argv) == 0
    assert calls == [f"{FIXTURE}:app"], command
