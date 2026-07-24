from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ENGINE_ROOT = ROOT / "pkgs" / "90_engines"
ALLOWED_BASES = {"EngineSession", "EngineSessionBase"}


def _base_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def test_engine_database_sessions_use_engine_session_base_contract() -> None:
    violations: list[str] = []
    for source in sorted(ENGINE_ROOT.glob("tigrbl_engine_*/src/**/*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not node.name.endswith("Session") or node.name.startswith(("_", "Async")):
                continue
            declared_bases = {_base_name(base) for base in node.bases}
            if declared_bases.isdisjoint(ALLOWED_BASES):
                bases = ", ".join(ast.unparse(base) for base in node.bases)
                violations.append(
                    f"{source.relative_to(ROOT)}:{node.lineno}: "
                    f"class {node.name}({bases})"
                )

    assert violations == []