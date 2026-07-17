# Tigrbl-required Pydantic parity

This matrix defines the bounded compatibility target for `tigrbl_model` before
any existing Tigrbl package migrates from Pydantic. The oracle is Pydantic v2;
the target is the behavior Tigrbl consumes, not every Pydantic extension point.

| Surface | Required behavior | Verification |
|---|---|---|
| `model_validate` | mappings, existing instances, coercion, strict mode, nested models | differential |
| `model_dump` | Python output, aliases, include/exclude, unset/default/null filtering | differential |
| `model_validate_json` | string, bytes, bytearray, structured syntax errors | differential + contract |
| `model_dump_json` | JSON-equivalent output and Tigrbl-used options | differential |
| `model_fields` | annotation, default, factory, aliases, required state, constraints | differential + unit |
| `model_config` | inheritance, extra policy, populate-by-name, schema extras | differential + unit |
| `model_construct` | validation bypass, defaults, fields-set tracking | differential |
| `model_rebuild` | explicit forward-reference namespace resolution | contract |
| `create_model` | dynamic fields, bases, config, required markers | differential + contract |
| `RootModel` | collection-root validation, dumping, JSON, schema | differential + contract |
| `model_json_schema` | object/root schemas, constraints, defaults, aliases, refs, custom ref template | differential + schema |
| field/model validators | before/after execution and invariant rejection | unit |
| JSON/YAML/TOML mixins | safe parsing and round trips through one model contract | serialization |
| legacy Serde aliases | `to_*`/`from_*` compatibility for spec dataclasses | serialization |

## Intentional boundaries

- The live-usage inventory covers active first-party package layers from
  `00_typing` through `95_client`. `99_deprecated` is recorded for later
  migration planning but is not part of this pre-migration certification gate.
- Pydantic plugin internals, core-schema hooks, computed fields, settings,
  dataclass decorators, and arbitrary third-party Pydantic plugins are outside
  this pre-migration target.
- Exact human-readable error prose and Pydantic documentation URLs are not a
  compatibility requirement. Error rejection, locations, and stable Tigrbl
  error categories are required.
- YAML and TOML methods are Tigrbl extensions. TOML serialization omits nulls
  because TOML has no null value.
