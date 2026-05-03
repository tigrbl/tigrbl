# SSE Kernel Packing KC and FastAPI Parity Report

- shared runner: httpx.ASGITransport
- raw bytes: 858
- compressed bytes: 374
- transport-only 250 ops/s: tigrbl=1212.51, fastapi=466.09
- db-backed 250 ops/s: tigrbl=744.95, fastapi=182.89
