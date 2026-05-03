# WebSocket Kernel Packing KC and FastAPI Parity Report

- shared runner: direct ASGI websocket session
- raw bytes: 848
- compressed bytes: 350
- transport-only 250 ops/s: tigrbl=14894.43, fastapi=28190.30
- db-backed 250 ops/s: tigrbl=179.67, fastapi=178.83
