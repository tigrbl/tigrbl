# Kernel Packing KC and FastAPI Parity Report

## Fairness
- primary comparison: fastapi.rest_unary vs tigrbl.rest_unary
- transport: HTTP REST unary
- request: POST /items
- payload: {"name": "string"}
- table: benchmark_item
- server runner: httpx.ASGITransport
- database: SQLite

## Throughput
- FastAPI REST unary: 131.80 ops/s
- Tigrbl REST unary: 718.12 ops/s
- Tigrbl JSON-RPC unary: 618.46 ops/s
- Tigrbl/FastAPI REST ratio: 5.448

## Tigrbl Kernel Packing KC Proxy
- raw bytes: 1627
- compressed bytes: 721
- segments: 38
- steps: 60
- phase tree nodes: 154
- compact steps: 60
- compact segments: 11
- compact program segment refs: 11
- compact route entries: 27
- shared error profiles: 2
- externalized prelude steps: 1
- max index width bits: 16
- compressed bytes per REST op in this run: 4.81
