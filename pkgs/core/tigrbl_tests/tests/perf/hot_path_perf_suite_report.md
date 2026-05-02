# Hot-Path Perf Suite

## Gates
- `REST unary > 425 ops/s`: PASS (628.40)
- `JSON-RPC unary > 400 ops/s`: PASS (564.28)
- `Unary TGPKHOT1 raw_bytes <= baseline`: PASS (1627 <= 1627)

## Throughput Summary
- unary: tigrbl REST=628.40, tigrbl JSON-RPC=564.28, fastapi REST=120.20
- streaming transport-only 250: tigrbl=1017.04, fastapi=417.56
- streaming db-backed 250: tigrbl=677.22, fastapi=168.01
- streaming TGPKHOT1: raw=858, compressed=374
- websocket transport-only 250: tigrbl=1251.02, fastapi=28504.97
- websocket db-backed 250: tigrbl=149.58, fastapi=174.22
- websocket TGPKHOT1: raw=848, compressed=350

## Tasks
- `kernel_plan_benchmark`: exit `0`
- `rest_unary_seq_25`: exit `0`
- `rest_unary_seq_250`: exit `0`
- `tigrbl_call_graph_250`: exit `0`
- `fastapi_call_graph_250`: exit `0`
- `streaming_perf_suite`: exit `0`
- `websocket_perf_suite`: exit `0`

## Artifacts
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\kernel-plan-benchmark.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\kernel-plan-benchmark.md`
- `E:\swarmauri_github\tigrbl\.tmp\kernel-plan-benchmark.json`
- `E:\swarmauri_github\tigrbl\.tmp\kernel-plan-benchmark.md`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\benchmark_results_create_uvicorn.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\benchmark_results_create_uvicorn_sequential_10_rounds.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\benchmark_results_create_uvicorn_sequential_10_rounds_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tigrbl_create_call_graph_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\fastapi_create_call_graph_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\benchmark_results_streaming_uvicorn.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\kernel-plan-benchmark-streaming.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\kernel-plan-benchmark-streaming.md`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tigrbl_streaming_call_graph_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\fastapi_streaming_call_graph_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-streaming.bin`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-streaming.summary.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-streaming.hexdump.txt`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-streaming.benchmark.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-streaming.benchmark.md`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\benchmark_results_websocket_uvicorn.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\kernel-plan-benchmark-websocket.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\kernel-plan-benchmark-websocket.md`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tigrbl_websocket_call_graph_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\fastapi_websocket_call_graph_250_ops.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-websocket.bin`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-websocket.summary.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-websocket.hexdump.txt`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-websocket.benchmark.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-websocket.benchmark.md`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-items.bin`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-items.summary.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-items.hexdump.txt`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-items.benchmark.json`
- `E:\swarmauri_github\tigrbl\pkgs\core\tigrbl_tests\tests\perf\tgpkhot1-benchmark-items.benchmark.md`
