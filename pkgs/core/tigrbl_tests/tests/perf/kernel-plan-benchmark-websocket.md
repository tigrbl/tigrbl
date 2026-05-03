# WebSocket Kernel Packing KC and FastAPI Parity Report

- shared runner: direct ASGI websocket session
- raw bytes: 848
- compressed bytes: 350
- transport-only 250 ops/s: tigrbl=12656.88, fastapi=27490.05
- db-backed 250 ops/s: tigrbl=175.99, fastapi=174.17
