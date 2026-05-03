# WebSocket Kernel Packing KC and FastAPI Parity Report

- shared runner: direct ASGI websocket session
- raw bytes: 848
- compressed bytes: 350
- transport-only 250 ops/s: tigrbl=14237.96, fastapi=27908.64
- db-backed 250 ops/s: tigrbl=156.41, fastapi=165.23
