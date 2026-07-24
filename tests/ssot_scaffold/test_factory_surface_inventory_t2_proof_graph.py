from pathlib import Path

from tigrbl_tests.factory_conformance import discover_factory_candidates, load_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = {
    REPO_ROOT / "pkgs/10_core/tigrbl_core/tigrbl_core": "tigrbl_core",
    REPO_ROOT / "pkgs/20_base/tigrbl_base/tigrbl_base": "tigrbl_base",
    REPO_ROOT / "pkgs/45_kernel/tigrbl_kernel/tigrbl_kernel": "tigrbl_kernel",
    REPO_ROOT / "pkgs/70_concrete/tigrbl_concrete/tigrbl_concrete": "tigrbl_concrete",
}


def _symbol_path(candidate) -> str:
    for root, package in SOURCE_ROOTS.items():
        try:
            relative = candidate.path.relative_to(root)
        except ValueError:
            continue
        module_parts = list(relative.with_suffix("").parts)
        if module_parts[-1] == "__init__":
            module_parts.pop()
        module = ".".join((package, *module_parts))
        return f"{module}:{candidate.qualname}"
    raise AssertionError(f"candidate outside configured production roots: {candidate.path}")


def test_production_factory_inventory_has_no_unregistered_candidates():
    registered = set(load_manifest().by_path())
    candidates = discover_factory_candidates(SOURCE_ROOTS)
    missing = sorted(
        symbol for candidate in candidates if (symbol := _symbol_path(candidate)) not in registered
    )
    assert missing == []
