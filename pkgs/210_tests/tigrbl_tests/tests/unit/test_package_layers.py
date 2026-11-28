from __future__ import annotations

from pathlib import Path
import re

from index_toml_contracts import load

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[5]
INDEX_PATH = ROOT / "index.toml"
PACKAGE_GLOBS = ("pkgs/*/*",)


def _normalize_distribution_name(name: str) -> str:
    return name.lower().replace("_", "-")


def _package_roots() -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for pattern in PACKAGE_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_dir() and (path / "pyproject.toml").exists():
                roots[path.name] = path
    return roots


def _internal_dependency_edges(package_roots: dict[str, Path]) -> list[tuple[str, str]]:
    distribution_to_package: dict[str, str] = {}
    for package, root in package_roots.items():
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        distribution_to_package[
            _normalize_distribution_name(pyproject["project"]["name"])
        ] = package

    edges: list[tuple[str, str]] = []
    for package, root in package_roots.items():
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        for dependency in pyproject["project"].get("dependencies", ()):
            dependency_name = re.split(r"[<>=!~;\[]", dependency, maxsplit=1)[0].strip()
            dependency_package = distribution_to_package.get(
                _normalize_distribution_name(dependency_name)
            )
            if dependency_package is not None:
                edges.append((package, dependency_package))
    return sorted(edges)


def test_package_layer_index_covers_every_workspace_package_once() -> None:
    package_roots = _package_roots()
    index = load(INDEX_PATH)
    layers = {layer["id"]: layer for layer in index["layers"]}

    assert {package["id"] for package in index["packages"]} == set(package_roots)
    assert {layer["path"] for layer in layers.values()} == {
        root.parent.relative_to(ROOT).as_posix() for root in package_roots.values()
    }

    for package in index["packages"]:
        package_root = package_roots[package["id"]]
        assert ROOT / package["path"] == package_root
        assert ROOT / layers[package["layer"]]["path"] == package_root.parent
        with (package_root / "pyproject.toml").open("rb") as manifest:
            assert tomllib.load(manifest)["project"]["name"] == package["name"]


def test_package_layer_orders_keep_key_framework_layers_separate() -> None:
    index = load(INDEX_PATH)
    for layer in index["layers"]:
        assert layer["path"] == f"pkgs/{layer['id']}"
        assert layer["id"].split("_", 1)[0] == f"{layer['order']:02d}"
        assert layer["same_layer_dependencies"] == "allowed"
        assert set(layer["allowed_dependency_layers"]) == {
            target["id"] for target in index["layers"] if target["order"] < layer["order"]
        }


def test_workspace_dependencies_follow_layer_direction_or_declared_exception() -> None:
    index = load(INDEX_PATH)
    packages = {package["id"]: package for package in index["packages"]}
    orders = {layer["id"]: layer["order"] for layer in index["layers"]}
    dependencies = set()
    exceptions = set()
    for source, package in packages.items():
        assert not package.get("dependency_exceptions"), source
        dependencies.update((source, target) for target in package.get("dependencies", []))
        reasons = package.get("metadata", {}).get("tigrbl", {}).get("legacy_dependency_exceptions", {})
        for target, reason in reasons.items():
            assert isinstance(reason, str) and reason.strip(), (source, target)
            assert orders[package["layer"]] < orders[packages[target]["layer"]], (source, target)
            exceptions.add((source, target))

    assert not dependencies & exceptions
    assert dependencies | exceptions == set(_internal_dependency_edges(_package_roots()))


def test_numba_route_dispatch_is_an_install_extra() -> None:
    package_roots = _package_roots()
    runtime = tomllib.loads(
        (package_roots["tigrbl_runtime"] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    facade = tomllib.loads(
        (package_roots["tigrbl"] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]

    for package in (runtime, facade):
        default_names = {
            _normalize_distribution_name(
                re.split(r"[<>=!~;\[]", entry, maxsplit=1)[0].strip()
            )
            for entry in package["dependencies"]
        }
        assert default_names.isdisjoint({"numba", "llvmlite", "numpy"})
    assert any(
        entry.startswith("numba>=")
        for entry in runtime["optional-dependencies"]["numba"]
    )
    assert any(
        entry.startswith("tigrbl-runtime[numba]>=")
        for entry in facade["optional-dependencies"]["numba"]
    )
