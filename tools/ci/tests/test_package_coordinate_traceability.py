from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / ".ssot" / "registry.json"
REPORT_PATH = REPO_ROOT / ".ssot" / "reports" / "package-coordinate-traceability-plan-2026-04-28.md"


def _project_names() -> set[str]:
    names: set[str] = set()
    for pyproject in (REPO_ROOT / "pkgs").rglob("pyproject.toml"):
        if "archive" in pyproject.parts:
            continue
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        name = data.get("project", {}).get("name")
        if isinstance(name, str) and name:
            names.add(name.replace("_", "-"))
    return names


def _registry_feature_text() -> str:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return "\n".join(
        " ".join(
            str(feature.get(key, ""))
            for key in ("id", "title", "description")
        )
        for feature in registry.get("features", [])
    ).replace("_", "-")


def test_package_coordinate_traceability_is_closed() -> None:
    feature_text = _registry_feature_text()
    missing = {
        name
        for name in _project_names()
        if name not in feature_text
    }

    assert not missing

    report = REPORT_PATH.read_text(encoding="utf-8")
    for name in sorted(_project_names()):
        assert f"`{name}`" in report
