# Tigrbl RestBulkCrudTable PostgreSQL Demo

This UV project shows the canonical Tigrbl authoring shape for a
PostgreSQL-backed `RestBulkCrudTable`.

The demo focuses on one resource:

- collection REST bulk CRUD at `/orders`
- member REST CRUD at `/orders/{item_id}`
- OpenAPI at `/openapi.json`

The app entrypoint is `examples/rest_bulk_crud_postgres_demo/app.py:build_app`.

## What The Demo Proves

- `RestBulkCrudTable` projects collection routes for `list`, `bulk_create`,
  `bulk_update`, `bulk_replace`, and `bulk_delete`
- member routes remain available for `read`, `update`, `replace`, and `delete`
- the default runtime backend is PostgreSQL through the public `pgs(...)`
  engine shortcut
- the app can still be tested locally with an engine override without changing
  the authored demo surface

## Runtime Configuration

The demo reads these environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_DSN` | unset | Full DSN override such as `postgresql+psycopg://user:pwd@host:5432/db` |
| `TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_HOST` | `127.0.0.1` | PostgreSQL host when `DSN` is not set |
| `TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_PORT` | `5432` | PostgreSQL port when `DSN` is not set |
| `TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_USER` | `tigrbl` | PostgreSQL user when `DSN` is not set |
| `TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_PASSWORD` | `tigrbl` | PostgreSQL password when `DSN` is not set |
| `TIGRBL_REST_BULK_CRUD_POSTGRES_DEMO_DB` | `tigrbl_rest_bulk_crud_demo` | PostgreSQL database when `DSN` is not set |

Copy `.env.example` if you want a ready-made local setup contract.

## Start PostgreSQL

The repo includes a small compose file for the demo database:

```powershell
cd .\examples\rest_bulk_crud_postgres_demo
docker compose up -d
```

## Serve The Demo

```powershell
uv run --project .\examples\rest_bulk_crud_postgres_demo python -m tigrbl serve .\examples\rest_bulk_crud_postgres_demo\app.py:build_app --server uvicorn --host 127.0.0.1 --port 8000
```

Useful surfaces:

- `http://127.0.0.1:8000/healthz`
- `http://127.0.0.1:8000/demo-config`
- `http://127.0.0.1:8000/openapi.json`

## Demo Calls

Bulk create:

```powershell
curl -X POST http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "[{\"id\":\"ord-100\",\"sku\":\"sku-100\",\"quantity\":2,\"status\":\"pending\"},{\"id\":\"ord-101\",\"sku\":\"sku-101\",\"quantity\":5,\"status\":\"pending\"}]"
```

Bulk update:

```powershell
curl -X PATCH http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "[{\"id\":\"ord-100\",\"quantity\":3},{\"id\":\"ord-101\",\"status\":\"allocated\"}]"
```

Bulk replace:

```powershell
curl -X PUT http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "[{\"id\":\"ord-100\",\"sku\":\"sku-100-r\",\"quantity\":7,\"status\":\"packed\"},{\"id\":\"ord-101\",\"sku\":\"sku-101-r\",\"quantity\":8,\"status\":\"packed\"}]"
```

List:

```powershell
curl http://127.0.0.1:8000/orders
```

Read one order:

```powershell
curl http://127.0.0.1:8000/orders/ord-100
```

Bulk delete:

```powershell
curl -X DELETE http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "{\"ids\":[\"ord-100\",\"ord-101\"]}"
```

## Test

```powershell
cd .\examples\rest_bulk_crud_postgres_demo
uv run pytest
```

The checked-in tests use a local engine override so they stay runnable without a
live PostgreSQL server. The authored app surface still defaults to PostgreSQL at
runtime.
