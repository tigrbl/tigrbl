from __future__ import annotations

from pathlib import Path
import compileall
import importlib
import importlib.util
import sys
from dataclasses import dataclass
from typing import Iterable


try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[3]
PKGS_ROOT = REPO_ROOT / "pkgs"


@dataclass(frozen=True)
class PackageRecord:
    name: str
    package_dir: Path
    pyproject_path: Path
    module_name: str


def _iter_active_pyprojects() -> Iterable[Path]:
    for path in sorted(PKGS_ROOT.rglob("pyproject.toml")):
        if "archive" in path.parts:
            continue
        if path.parent.name == "__pycache__":
            continue
        if path.parent == PKGS_ROOT:
            continue
        yield path


def _discover_package_modules() -> list[PackageRecord]:
    records: list[PackageRecord] = []
    for pyproject_path in _iter_active_pyprojects():
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        name = project.get("name")
        if not isinstance(name, str) or not name:
            continue

        module_name = name.replace("-", "_")
        candidate = pyproject_path.parent / module_name
        if candidate.is_dir() and (candidate / "__init__.py").exists():
            package_dir = candidate
        else:
            package_dirs = [
                path
                for path in pyproject_path.parent.iterdir()
                if path.is_dir()
                and (path / "__init__.py").exists()
                and path.name != "docs"
                and path.name != "tests"
            ]
            package_dir = package_dirs[0] if package_dirs else pyproject_path.parent
        records.append(PackageRecord(name=name, package_dir=package_dir, pyproject_path=pyproject_path, module_name=module_name))
    return records


def _clear_unspecced_stub(module_name: str) -> None:
    module = sys.modules.get(module_name)
    if module is None or getattr(module, "__spec__", None) is not None:
        return

    prefix = f"{module_name}."
    for loaded_name in list(sys.modules):
        if loaded_name == module_name or loaded_name.startswith(prefix):
            sys.modules.pop(loaded_name, None)


def test_all_packages_buildable_and_importable() -> None:
    failures: list[tuple[str, str]] = []
    records = _discover_package_modules()
    assert records, "No package records discovered under pkgs/"

    for record in records:
        source_root = record.pyproject_path.parent
        if str(source_root) not in sys.path:
            sys.path.insert(0, str(source_root))

        if not compileall.compile_dir(
            str(record.package_dir),
            quiet=1,
            legacy=True,
        ):
            failures.append((record.name, f"compile failure in {record.package_dir}"))
            continue

        _clear_unspecced_stub(record.module_name)
        if importlib.util.find_spec(record.module_name) is None:
            failures.append((record.name, f"module '{record.module_name}' not importable from {source_root}"))
            continue

        try:
            importlib.import_module(record.module_name)
        except Exception as exc:
            failures.append((record.name, f"import failure: {exc}"))

    assert not failures, "Package buildability/importability failures:\n" + "\n".join(
        f"- {name}: {reason}" for name, reason in failures
    )
