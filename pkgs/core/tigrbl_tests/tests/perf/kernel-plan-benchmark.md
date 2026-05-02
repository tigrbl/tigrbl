# Kernel Packing KC and FastAPI Parity Report

## Fairness
- primary comparison: fastapi.rest_unary vs tigrbl.rest_unary
- transport: HTTP REST unary
- request: POST /items
- payload: {"name": "string"}
- table: benchmark_item
- server runner: uvicorn via run_uvicorn_in_task
- database: SQLite

## Throughput
- FastAPI REST unary: 119.83 ops/s
- Tigrbl REST unary: 285.31 ops/s
- Tigrbl JSON-RPC unary: 273.71 ops/s
- Tigrbl/FastAPI REST ratio: 2.381

## Tigrbl Kernel Packing KC Proxy
- raw bytes: 1679
- compressed bytes: 730
- segments: 38
- steps: 60
- phase tree nodes: 504
- compact steps: 60
- compact segments: 11
- compact program segment refs: 36
- compact route entries: 49
- shared error profiles: 2
- externalized prelude steps: 1
- max index width bits: 16
- compressed bytes per REST op in this run: 4.87
