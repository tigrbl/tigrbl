# tigrbl_engine_mariadb

The MariaDB engine plugin for Tigrbl. It registers the `mariadb` engine kind and
returns Tigrbl `EngineSession` instances backed by SQLAlchemy and PyMySQL.

```python
from tigrbl.factories.engine import mariadb

engine = mariadb(user="portwyrm", pwd="secret", name="portwyrm")
```

