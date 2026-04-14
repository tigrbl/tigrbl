from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_repo_paths() -> Path:
    root = Path(__file__).resolve().parents[2]
    extra_paths = [root / ".vendor"]
    extra_paths.extend(
        path
        for path in (root / ".uv-cache" / "archive-v0").glob("*/Lib/site-packages")
        if path.is_dir()
    )
    for candidate in extra_paths:
        path = str(candidate)
        if candidate.is_dir() and path not in sys.path:
            sys.path.insert(0, path)
    for base in (root / "pkgs" / "core", root / "pkgs" / "engines"):
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir():
                continue
            for candidate in (child, child / "src"):
                if candidate.is_dir():
                    path = str(candidate)
                    if path not in sys.path:
                        sys.path.insert(0, path)
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


REPO_ROOT = _bootstrap_repo_paths()

from sqlalchemy import String  # noqa: E402

from tigrbl_base._base import AppBase, ColumnBase, TableBase  # noqa: E402
from tigrbl_core._spec.app_spec import AppSpec  # noqa: E402
from tigrbl_core._spec.binding_spec import (  # noqa: E402
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
)
from tigrbl_core._spec.engine_spec import EngineSpec  # noqa: E402
from tigrbl_core._spec.op_spec import OpSpec  # noqa: E402
from tigrbl_core._spec.storage_spec import StorageSpec  # noqa: E402
from tigrbl_runtime.native.codec import build_native_app_spec  # noqa: E402


class DemoUser(TableBase):
    __tablename__ = "users"
    __resource__ = "users"

    id = ColumnBase(storage=StorageSpec(type_=String, primary_key=True))
    name = ColumnBase(storage=StorageSpec(type_=String))

    __tigrbl_ops__ = (
        OpSpec(
            alias="users.create",
            target="create",
            arity="collection",
            expose_rpc=False,
            expose_method=False,
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("POST",),
                    path="/users",
                ),
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="users.create",
                ),
            ),
            tx_scope="read_write",
        ),
        OpSpec(
            alias="users.read",
            target="read",
            arity="member",
            expose_rpc=False,
            expose_method=False,
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("GET",),
                    path="/users/{id}",
                ),
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="users.read",
                ),
            ),
            tx_scope="read_only",
        ),
    )


class NativeRuntimeDemoApp(AppBase):
    TITLE = "native_runtime_demo"
    VERSION = "0.1.0"
    DESCRIPTION = "Python-authored Tigrbl AppSpec executed by the Rust-native runtime."
    EXECUTION_BACKEND = "rust"
    ENGINE = EngineSpec.from_any({"kind": "sqlite", "mode": "memory", "async": False})
    TABLES = (DemoUser,)


def compose_app_spec() -> AppSpec:
    return AppBase.collect_spec(NativeRuntimeDemoApp)


def build_native_payload() -> dict[str, object]:
    return build_native_app_spec(compose_app_spec())


__all__ = [
    "DemoUser",
    "NativeRuntimeDemoApp",
    "REPO_ROOT",
    "build_native_payload",
    "compose_app_spec",
]
