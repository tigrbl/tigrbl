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
