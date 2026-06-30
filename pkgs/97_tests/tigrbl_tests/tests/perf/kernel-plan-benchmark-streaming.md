# Streaming Kernel Packing KC and FastAPI Parity Report

- shared runner: httpx.ASGITransport
- raw bytes: 858
- compressed bytes: 374
- transport-only 250 ops/s: tigrbl=1281.21, fastapi=561.02
- db-backed 250 ops/s: tigrbl=803.75, fastapi=215.28
