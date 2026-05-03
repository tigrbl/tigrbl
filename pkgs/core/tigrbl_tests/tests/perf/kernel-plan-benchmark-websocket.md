# WebSocket Kernel Packing KC and FastAPI Parity Report

- shared runner: direct ASGI websocket session
- raw bytes: 848
- compressed bytes: 350
- transport-only 250 ops/s: tigrbl=14971.14, fastapi=27217.40
- db-backed 250 ops/s: tigrbl=163.10, fastapi=159.50
