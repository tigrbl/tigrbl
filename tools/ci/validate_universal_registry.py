from __future__ import annotations

import json

from common import fail, repo_relative
from registry_model import REGISTRY_DIR, build_universal_registry


def main() -> None:
    errors: list[str] = []
    target = REGISTRY_DIR / "universal_registry.json"
    target_rel = repo_relative(target)
    if not target.exists():
        errors.append(f"{target_rel} is missing")
        fail(errors)
        return

    expected = build_universal_registry()
    current = json.loads(target.read_text(encoding="utf-8"))
    if current != expected:
        errors.append(
            f"{target_rel} is out of date; run python tools/ci/build_universal_registry.py"
        )

    fail(errors)
    print("Universal registry validation passed")


if __name__ == "__main__":
    main()
