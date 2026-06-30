from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[6]
BENCHMARK_PATH = (
    ROOT
    / "pkgs/97_tests/tigrbl_tests/tests/perf/test_fastapi_vs_tigrbl_executor_benchmark.py"
)


def _assigned_tuple(tree: ast.AST, name: str) -> tuple[str, ...]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if not isinstance(node.value, ast.Tuple):
            raise AssertionError(f"{name} must be a tuple literal")
        values = []
        for item in node.value.elts:
            if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
                raise AssertionError(f"{name} must contain only string literals")
            values.append(item.value)
        return tuple(values)
    raise AssertionError(f"{name} assignment not found")


def test_required_benchmark_scenarios_are_python_only() -> None:
    source = BENCHMARK_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    scenarios = _assigned_tuple(tree, "SCENARIOS")

    assert scenarios == ("fastapi", "tigrbl_python_executor")
    assert all("rust" not in scenario.lower() for scenario in scenarios)
    assert "tigrbl_rust_executor" not in source
