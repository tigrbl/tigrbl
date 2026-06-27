from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_boundary_artifacts_exist():
    required_paths = [
        "pkgs/core/tigrbl_runtime/BOUNDARY.yaml",
        "pkgs/core/tigrbl_runtime/AGENTS.md",
        "tools/ci/validate_runtime_boundary.py",
        "pkgs/core/tigrbl_runtime/tests/test_runtime_boundary_contract.py",
        ".github/workflows/gate-runtime-boundary.yml",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []
