from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "pkgs" / "core" / "tigrbl_core" / "schemas"
BUNDLE_PATH = SCHEMA_DIR / "bundle.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rewrite_refs(value: Any) -> Any:
    if isinstance(value, dict):
        rewritten = {key: _rewrite_refs(item) for key, item in value.items()}
        ref = rewritten.get("$ref")
        if isinstance(ref, str):
            if ref.startswith("./shared.json#/$defs/"):
                name = ref.rsplit("/", 1)[-1]
                rewritten["$ref"] = f"#/$defs/{name}"
            elif ref.startswith("./") and ref.endswith(".json"):
                name = ref[2:-5]
                rewritten["$ref"] = f"#/$defs/{name}"
            elif ref.startswith("./") and ".json#/$defs/" in ref:
                file_part, _, def_part = ref.partition("#/$defs/")
                schema_name = file_part[2:-5]
                if def_part == f"{schema_name}Envelope":
                    rewritten["$ref"] = f"#/$defs/{def_part}"
        return rewritten
    if isinstance(value, list):
        return [_rewrite_refs(item) for item in value]
    return value


def build_bundle(schema_dir: Path = SCHEMA_DIR) -> dict[str, Any]:
    shared_path = schema_dir / "shared.json"
    shared = _load_json(shared_path)

    defs: dict[str, Any] = {
        name: _rewrite_refs(schema)
        for name, schema in (shared.get("$defs") or {}).items()
    }

    schemas: dict[str, str] = {}
    for path in sorted(schema_dir.glob("*.json")):
        if path.name in {"shared.json", "bundle.json"}:
            continue
        schema = _load_json(path)
        spec_name = path.stem
        schemas[spec_name] = f"#/$defs/{spec_name}"

        root_schema = {
            key: _rewrite_refs(value)
            for key, value in schema.items()
            if key not in {"$schema", "$id", "$defs"}
        }
        defs[spec_name] = root_schema

        local_defs = schema.get("$defs") or {}
        for def_name, def_schema in local_defs.items():
            defs[def_name] = _rewrite_refs(def_schema)

    return {
        "$schema": shared["$schema"],
        "$id": "bundle.json",
        "title": "Tigrbl Core Spec Schema Bundle",
        "schemas": schemas,
        "$defs": defs,
    }


def main() -> int:
    bundle = build_bundle()
    BUNDLE_PATH.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
