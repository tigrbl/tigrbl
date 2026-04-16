from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT / "pkgs" / "core" / "tigrbl_core" / "tigrbl_core" / "schema" / "spec_json.py"
)
OUTPUT_DIR = ROOT / "pkgs" / "core" / "tigrbl_core" / "schemas"


def _load_spec_json_module():
    spec = importlib.util.spec_from_file_location("tigrbl_core_spec_json", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = _load_spec_json_module()
    shared_schema = module.build_shared_json_schema()
    schemas = module.build_individual_spec_json_schemas()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shared_out_path = OUTPUT_DIR / module.SHARED_SCHEMA_NAME
    shared_out_path.write_text(
        json.dumps(shared_schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for spec_name, schema in schemas.items():
        out_path = OUTPUT_DIR / f"{spec_name}.json"
        out_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
