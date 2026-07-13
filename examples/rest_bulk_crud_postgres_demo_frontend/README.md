# Tigrbl RestBulkCrudTable Postgres Demo Frontend

Static Vite/React console for the PostgreSQL-backed Tigrbl REST demo. The UI showcases the real `orders` table shape and exercises collection, single-member, and bulk REST endpoints through the Docker nginx proxy.

## Run With Docker

From the repository root:

```powershell
docker compose -f .\examples\rest_bulk_crud_postgres_demo\compose.yaml up -d --build
```

Then open:

- Frontend: http://127.0.0.1:8002/
- Backend OpenAPI: http://127.0.0.1:8001/docs
- Backend config: http://127.0.0.1:8001/demo-config

## Local Frontend Development

```powershell
cd examples\rest_bulk_crud_postgres_demo_frontend
npm install
npm run dev
```

The Docker build serves the app through nginx and proxies `/api/*` to the backend service.
