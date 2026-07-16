# tigrbl_engine_mysql

The MySQL engine plugin for Tigrbl. It registers the `mysql` engine kind and
returns Tigrbl `EngineSession` instances backed by SQLAlchemy and PyMySQL.

```python
from tigrbl.factories.engine import mysql

engine = mysql(user="portwyrm", pwd="secret", name="portwyrm")
```

