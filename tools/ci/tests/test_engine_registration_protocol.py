from __future__ import annotations

import ast
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = REPO_ROOT / "pkgs" / "90_engines"
CANONICAL_GROUP = "tigrbl.engine_plugins"
LEGACY_GROUP = "tigrbl.engine"


def _entry_points(pyproject: Path) -> dict[str, dict[str, str]]:
    with pyproject.open("rb") as stream:
        document = tomllib.load(stream)
    return document.get("project", {}).get("entry-points", {})


def _entry_point_source(package_dir: Path, target: str) -> Path:
    module_name, separator, attribute = target.partition(":")
    assert separator and attribute == "register", (
        f"{package_dir.name}: engine entry points must target a register function"
    )
    module_path = package_dir / "src" / Path(*module_name.split("."))
    source = module_path.with_suffix(".py")
    if not source.is_file():
        source = module_path / "__init__.py"
    assert source.is_file(), f"{package_dir.name}: missing entry-point source {source}"
    return source


def _registration_class(tree: ast.Module, source: Path) -> ast.ClassDef:
    registration = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "_Registration"
        ),
        None,
    )
    assert registration is not None, (
        f"{source}: register an object implementing EngineRegistration"
    )
    return registration


def _method(registration: ast.ClassDef, name: str, source: Path) -> ast.FunctionDef:
    method = next(
        (
            node
            for node in registration.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )
    assert method is not None, f"{source}: _Registration must implement {name}()"
    return method


def test_all_engines_use_current_registration_protocol() -> None:
    packages = sorted(path for path in ENGINE_ROOT.iterdir() if path.is_dir())
    assert packages, "engine package inventory must not be empty"

    checked_sources: set[Path] = set()
    for package_dir in packages:
        pyproject = package_dir / "pyproject.toml"
        groups = _entry_points(pyproject)
        assert LEGACY_GROUP not in groups, (
            f"{package_dir.name}: use canonical {CANONICAL_GROUP!r} entry points"
        )
        registrations = groups.get(CANONICAL_GROUP)
        assert registrations, (
            f"{package_dir.name}: missing canonical engine registration entry point"
        )

        for target in registrations.values():
            source = _entry_point_source(package_dir, target)
            if source in checked_sources:
                continue
            checked_sources.add(source)

            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            registration = _registration_class(tree, source)
            build = _method(registration, "build", source)
            capabilities = _method(registration, "capabilities", source)

            assert [arg.arg for arg in build.args.kwonlyargs] == [
                "mapping",
                "spec",
                "dsn",
            ], f"{source}: build() must accept keyword-only mapping, spec, and dsn"
            assert [arg.arg for arg in capabilities.args.kwonlyargs] == [
                "spec",
                "mapping",
            ], f"{source}: capabilities() must accept keyword-only spec and mapping"

            register = next(
                (
                    node
                    for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "register"
                ),
                None,
            )
            assert register is not None, f"{source}: missing register() entry point"
            calls = [
                node
                for node in ast.walk(register)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "register_engine"
            ]
            assert calls, f"{source}: register() must call register_engine()"
            assert all(len(call.args) == 2 and not call.keywords for call in calls), (
                f"{source}: register_engine() requires kind and EngineRegistration only"
            )
