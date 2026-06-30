# SSE Kernel Packing KC and FastAPI Parity Report

- shared runner: httpx.ASGITransport
- raw bytes: 858
- compressed bytes: 374
- transport-only 250 ops/s: tigrbl=1273.31, fastapi=457.12
- db-backed 250 ops/s: tigrbl=775.13, fastapi=188.14
