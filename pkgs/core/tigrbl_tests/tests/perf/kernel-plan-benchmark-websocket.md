# WebSocket Kernel Packing KC and FastAPI Parity Report

- shared runner: direct ASGI websocket session
- raw bytes: 848
- compressed bytes: 350
- transport-only 250 ops/s: tigrbl=1251.02, fastapi=28504.97
- db-backed 250 ops/s: tigrbl=149.58, fastapi=174.22
