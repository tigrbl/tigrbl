from __future__ import annotations

import json

from registry_model import REGISTRY_DIR, ROOT, build_universal_registry


def main() -> None:
    registry = build_universal_registry()
    path = REGISTRY_DIR / "universal_registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
