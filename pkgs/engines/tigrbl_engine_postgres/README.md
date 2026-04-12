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
