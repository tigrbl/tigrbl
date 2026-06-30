from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tigrbl_core._spec import AppSpec, PathSpec, RouterSpec


REPO_ROOT = Path(__file__).resolve().parents[5]


def test_routespec_is_not_a_public_canonical_spec_export() -> None:
    import tigrbl_core._spec as spec

    assert not hasattr(spec, "RouteSpec")
    assert "RouteSpec" not in getattr(spec, "__all__", ())


def test_appspec_and_routerspec_reject_legacy_routes_field() -> None:
    with pytest.raises(ValueError, match="AppSpec does not accept 'routes'"):
        AppSpec.from_dict({"routes": []})

    with pytest.raises(ValueError, match="RouterSpec does not accept 'routes'"):
        RouterSpec.from_dict({"routes": []})

    with pytest.raises(ValueError, match="PathSpec does not accept 'routes'"):
        PathSpec.from_dict({"path": "/items", "routes": []})

    router = RouterSpec(name="api", paths=(PathSpec(path="/items", kind="resource"),))

    assert router.paths[0].path == "/items"


def test_canonical_spec_package_does_not_import_legacy_route_module() -> None:
    spec_root = REPO_ROOT / "pkgs" / "core" / "tigrbl_core" / "tigrbl_core" / "_spec"
    offenders: list[str] = []
    for py_file in spec_root.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.endswith("._route") or module.endswith("_concrete._route"):
                    offenders.append(str(py_file.relative_to(REPO_ROOT)))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.endswith("._route") or alias.name.endswith(
                        "_concrete._route"
                    ):
                        offenders.append(str(py_file.relative_to(REPO_ROOT)))

    assert offenders == []
