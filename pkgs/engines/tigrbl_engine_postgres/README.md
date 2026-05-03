# tigrbl_engine_postgres

PostgreSQL engine plugin for **Tigrbl**.

## Install

```bash
pip install tigrbl_engine_postgres
```

## Use

```python
from tigrbl.engine.decorators import engine_ctx

@engine_ctx({"kind": "postgres", "dsn": "postgresql+psycopg://user:pwd@localhost:5432/app"})
class AppAPI:
    pass
```

The plugin auto-registers via the `tigrbl.engine` entry point.
## Canonical documentation

This file is a package-local distribution entry point. Authoritative workspace guidance lives in:

- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package identity

- canonical repository: `https://github.com/tigrbl/tigrbl`
- organization: `https://github.com/tigrbl`
- social: `https://discord.gg/K4YTAPapjR`
- package path: `https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_postgres`
