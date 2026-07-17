<div align="center">
<h1>tigrbl_model</h1>
<p><strong>Pydantic-independent model validation, schema generation, and JSON, YAML, and TOML serialization for Tigrbl.</strong></p>
<a href="https://pypi.org/project/tigrbl-model/"><img src="https://img.shields.io/pypi/v/tigrbl-model?label=PyPI" alt="PyPI version for tigrbl_model"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_model"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl_model"/></a>
</div>

## What is tigrbl_model?

`tigrbl_model` is Tigrbl's Pydantic-independent model engine. It owns field metadata, validation, serialization, dynamic model construction, forward-reference rebuilding, and JSON Schema generation.

## Why use tigrbl_model?

Use it when code needs the Pydantic v2 surface certified for Tigrbl without taking a runtime dependency on Pydantic.

## When should I install tigrbl_model?

Install it when building Tigrbl extensions, reusable schema models, or applications that need the same model contract as Tigrbl.

## Who is tigrbl_model for?

Tigrbl maintainers, extension authors, and application developers who need validated models and portable serialization.

## Where does tigrbl_model fit?

It is a foundational package under `pkgs/02_model`, below Tigrbl packages that consume models, validation, and JSON Schema.

## How does tigrbl_model work?

Type annotations and `Field` metadata are compiled into an internal field graph. The graph drives validation, dumping, JSON Schema, and the JSON, YAML, and TOML mixins.

## Install

```bash
uv add tigrbl-model
```

```bash
pip install tigrbl-model
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | `tigrbl-model` |
| Repository path | `pkgs/02_model/tigrbl_model` |
| Python import root | `tigrbl_model` |
| Console scripts | none |
| Public mixins | `JsonMixin`, `YamlMixin`, `TomlMixin`, `SerdeMixin` |
| Runtime Pydantic dependency | none |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

- Runtime model construction and field metadata.
- Annotation-driven validation and structured errors.
- Dictionary and JSON serialization.
- JSON Schema generation.
- Independently composable JSON, YAML, and TOML mixins.
- `SerdeMixin`, which aggregates all three format mixins.

## Public API and Import Surface

The primary imports are `Model`/`BaseModel`, `RootModel`, `Field`, `ConfigDict`, `ValidationError`, `create_model`, `field_validator`, `model_validator`, and the four serialization mixins. See `tigrbl_model.__all__` for the complete certified surface.

## Usage Examples

```python
from tigrbl_model import Field, Model

class Widget(Model):
    name: str
    quantity: int = Field(default=0, ge=0)

widget = Widget.model_validate_json('{"name":"bolt","quantity":2}')
assert widget.model_dump() == {"name": "bolt", "quantity": 2}
assert Widget.model_validate_yaml(widget.model_dump_yaml()) == widget
assert Widget.model_validate_toml(widget.model_dump_toml()) == widget
```

Plain dataclasses can inherit `SerdeMixin` when validation and schema-model behavior are unnecessary.

## How To Choose This Package

Choose `tigrbl_model` for the focused model and serialization boundary. Choose the `tigrbl` facade when building a complete API application. Keep Pydantic installed only when independently comparing behavior during development.

## Related Packages

- `tigrbl`
- `tigrbl-core`
- `tigrbl-base`
- `tigrbl-runtime`

## Documentation Links

- [Certified parity boundary](PARITY.md)
- [Workspace documentation](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR)
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)

## Certification Status

The package's automated suite compares the supported contract with Pydantic v2 and scans first-party Tigrbl runtime usage. `PARITY.md` records intentional boundaries; Pydantic is a development-only parity oracle and is not a runtime dependency.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
