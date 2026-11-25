from __future__ import annotations

import ast
import importlib.metadata
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "tigrbl_concrete"
PYPROJECT = PACKAGE_ROOT / "pyproject.toml"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".", maxsplit=1)[0])
    return modules


def test_concrete_package_keeps_kernel_imports_out_of_all_modules() -> None:
    violations = [
        str(path.relative_to(PACKAGE_ROOT))
        for path in SOURCE_ROOT.rglob("*.py")
        if "tigrbl_kernel" in _imports(path)
    ]

    assert violations == []


def test_concrete_declares_runtime_dependency_without_kernel_dependency() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")

    assert '"tigrbl-runtime>=0.4.5.dev7"' in text
    assert '"tigrbl-kernel"' not in text


def test_installed_concrete_distribution_metadata_omits_kernel_dependency() -> None:
    requirements = importlib.metadata.requires("tigrbl-concrete") or []
    normalized = {re.split(r"[<>=!~; \[]", req, maxsplit=1)[0] for req in requirements}

    assert "tigrbl-runtime" in normalized
    assert "tigrbl-kernel" not in normalized


def test_concrete_authoring_and_lowering_modules_do_not_import_runtime() -> None:
    authoring_roots = (
        SOURCE_ROOT / "factories",
        SOURCE_ROOT / "shortcuts",
        SOURCE_ROOT / "_decorators",
        SOURCE_ROOT / "_mapping" / "appspec",
    )
    authoring_files = [
        path
        for root in authoring_roots
        for path in root.rglob("*.py")
        if path.exists()
    ]
    authoring_files.append(SOURCE_ROOT / "webhooks.py")

    violations = [
        str(path.relative_to(PACKAGE_ROOT))
        for path in authoring_files
        if "tigrbl_runtime" in _imports(path)
    ]

    assert violations == []


def test_camelcase_define_make_derive_authoring_surfaces_are_not_runtime_owned() -> None:
    runtime_root = PACKAGE_ROOT.parent / "tigrbl_runtime" / "tigrbl_runtime"
    runtime_exports: list[tuple[str, str]] = []
    for path in runtime_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith(("Make", "Define", "Derive")):
                    runtime_exports.append(
                        (str(path.relative_to(runtime_root)), node.name)
                    )

    assert runtime_exports == []


def test_concrete_lowering_services_reuse_declared_runtime_bridge() -> None:
    from tigrbl_concrete._runtime_services import compile_opview_from_specs
    from tigrbl_runtime.lowering_services import compile_opview_from_specs as runtime_compile

    from tigrbl_concrete._runtime_services import callback_hook_phases
    from tigrbl_kernel.callbacks import callback_hook_phases as kernel_callback_phases

    assert compile_opview_from_specs is runtime_compile
    assert callback_hook_phases is kernel_callback_phases


def test_concrete_rpc_fallback_does_not_inspect_transport_responses() -> None:
    path = SOURCE_ROOT / "_mapping" / "router" / "rpc.py"
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    fields = {node.value for node in ast.walk(tree)
              if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    assert fields.isdisjoint({"websocket", "body", "body_iterator", "status_code", "transport_response"})
    assert not any(
        isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("tigrbl_ops_oltp")
        and any(alias.name in {"ops", "bulk", "delete"} for alias in node.names)
        for node in ast.walk(tree)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["empty", "application-payload", "denied", "unknown"])
async def test_router_consumes_one_authoritative_invocation_outcome(monkeypatch, case):
    from tigrbl_concrete._mapping.router import rpc

    class Record:
        pass

    async def bind(payload, *, db, request, ctx):
        return {"model": Record, "alias": "delete", "ctx": ctx, "serialize": None,
                "request": request, "db": db}

    result = {"body": "application data", "status_code": 200, "deleted": 0} if case == "application-payload" else None
    failure = PermissionError("denied") if case == "denied" else LookupError("unknown") if case == "unknown" else None
    calls = []

    async def invoke(**kwargs):
        calls.append(kwargs["alias"])
        if failure is not None:
            raise failure
        return result

    Record.rpc = SimpleNamespace(delete=bind)
    monkeypatch.setattr(rpc, "_ensure_router_ns", lambda router: None)
    monkeypatch.setattr(rpc, "_fallback_resolution", lambda *args: SimpleNamespace(model=Record, target="delete"))
    monkeypatch.setattr(rpc, "_single_pk_name", lambda model: "id")
    monkeypatch.setattr(rpc, "invoke_op", invoke)
    if failure is not None:
        with pytest.raises(type(failure), match=case):
            await rpc.rpc_call(SimpleNamespace(), Record, "delete", {"id": 1}, db=object())
    else:
        assert await rpc.rpc_call(SimpleNamespace(), Record, "delete", {"id": 1}, db=object()) == result
    assert calls == ["delete"]
