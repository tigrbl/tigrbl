# tigrbl_engine_sqlite

SQLite engine plugin for **Tigrbl**.

## Install

```bash
pip install tigrbl_engine_sqlite
```

## Use

```python
from tigrbl.engine.decorators import engine_ctx

@engine_ctx({"kind": "sqlite", "path": "./data/app.db"})
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

