from __future__ import annotations

from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[5]
LAYERS_PATH = ROOT / "pkgs" / "LAYERS.toml"
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


def _load_layers() -> dict:
    return tomllib.loads(LAYERS_PATH.read_text(encoding="utf-8"))


def _package_layer_map(layers_doc: dict) -> dict[str, dict]:
    package_layers: dict[str, dict] = {}
    for layer in layers_doc["layer"]:
        for package in layer["packages"]:
            assert package not in package_layers, package
            package_layers[package] = layer
    return package_layers


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
    layers_doc = _load_layers()
    package_layers = _package_layer_map(layers_doc)

    assert set(package_layers) == set(package_roots)

    for package, layer in package_layers.items():
        package_root = ROOT / layer["path"] / package
        assert package_root == package_roots[package]
        assert (package_root / "pyproject.toml").is_file()


def test_package_layer_orders_keep_key_framework_layers_separate() -> None:
    package_layers = _package_layer_map(_load_layers())

    assert package_layers["tigrbl_typing"]["order"] == 0
    assert package_layers["tigrbl_spec"]["order"] == 1
    assert package_layers["tigrbl_core"]["order"] == 10
    assert package_layers["tigrbl_base"]["order"] == 20
    assert package_layers["tigrbl_orm"]["order"] == 30


def test_workspace_dependencies_follow_layer_direction_or_declared_exception() -> None:
    layers_doc = _load_layers()
    package_roots = _package_roots()
    package_layers = _package_layer_map(layers_doc)
    exceptions = {
        (item["package"], item["dependency"])
        for item in layers_doc.get("dependency_exception", ())
    }

    violations: list[str] = []
    for package, dependency in _internal_dependency_edges(package_roots):
        package_order = package_layers[package]["order"]
        dependency_order = package_layers[dependency]["order"]
        if dependency_order <= package_order:
            continue
        if (package, dependency) in exceptions:
            continue
        violations.append(
            f"{package} layer {package_order} depends on "
            f"{dependency} layer {dependency_order}"
        )

    assert violations == []


def test_declared_layer_dependency_exceptions_are_still_real_edges() -> None:
    layers_doc = _load_layers()
    package_roots = _package_roots()
    edges = set(_internal_dependency_edges(package_roots))

    stale = [
        (item["package"], item["dependency"])
        for item in layers_doc.get("dependency_exception", ())
        if (item["package"], item["dependency"]) not in edges
    ]

    assert stale == []


def test_engine_database_sessions_use_engine_session_base_contract() -> None:
    engine_roots = [
        root
        for name, root in _package_roots().items()
        if name.startswith("tigrbl_engine_")
    ]
    allowed_bases = {"EngineSessionBase", "EngineSession"}
    violations: list[str] = []
    class_pattern = re.compile(r"^class\s+([A-Za-z][A-Za-z0-9_]*Session)\(([^)]*)\):")

    for root in engine_roots:
        for source in (root / "src").rglob("*.py"):
            for line in source.read_text(encoding="utf-8").splitlines():
                match = class_pattern.match(line.strip())
                if not match:
                    continue
                class_name, bases = match.groups()
                if class_name.startswith("_") or class_name.startswith("Async"):
                    continue
                declared_bases = {
                    part.strip().split(".")[-1] for part in bases.split(",")
                }
                if declared_bases.isdisjoint(allowed_bases):
                    violations.append(f"{source.relative_to(ROOT)}: {line.strip()}")

    assert violations == []
