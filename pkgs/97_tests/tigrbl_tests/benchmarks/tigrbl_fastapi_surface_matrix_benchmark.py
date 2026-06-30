from __future__ import annotations

import argparse
import asyncio
import json
import random
import sqlite3
from pathlib import Path
from statistics import mean, median, pstdev
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Awaitable, Callable

import httpx
from fastapi import FastAPI, Request as FastAPIRequest

from tigrbl import Request as TigrblRequest
from tigrbl import TigrblApp
from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_fastapi_create_app import (
    create_fastapi_app,
    dispose_fastapi_app,
    fetch_fastapi_names,
)
from tests.perf.helper_streaming_apps import (
    create_fastapi_streaming_db_app,
    create_fastapi_streaming_transport_app,
    create_tigrbl_streaming_db_app,
    create_tigrbl_streaming_transport_app,
    expected_db_stream_bytes,
    expected_transport_stream_bytes,
)
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    dispose_tigrbl_app,
    fetch_tigrbl_names,
    initialize_tigrbl_app,
    tigrbl_create_path,
    tigrbl_create_rpc_method,
)
from tests.perf.helper_websocket_apps import (
    create_fastapi_websocket_db_app,
    create_fastapi_websocket_transport_app,
    create_tigrbl_websocket_db_app,
    create_tigrbl_websocket_transport_app,
    dispose_tigrbl_websocket_app,
    fetch_websocket_names,
    initialize_tigrbl_websocket_app,
)


ROOT = Path(__file__).resolve().parents[4]
PERF_DIR = ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "perf"
DEFAULT_JSON_OUTPUT = PERF_DIR / "benchmark_results_surface_matrix_25x250.json"
DEFAULT_MD_OUTPUT = PERF_DIR / "benchmark_results_surface_matrix_25x250.md"
DEFAULT_TMP_ROOT = ROOT / ".tmp" / "surface-matrix-25x250"
DEFAULT_ROUNDS = 25
DEFAULT_OPS = 250
DEFAULT_WARMUP_OPS = 5
TMP_ROOT = DEFAULT_TMP_ROOT
OUT_JSON = DEFAULT_JSON_OUTPUT
OUT_MD = DEFAULT_MD_OUTPUT
ROUNDS = DEFAULT_ROUNDS
OPS = DEFAULT_OPS
WARMUP_OPS = DEFAULT_WARMUP_OPS
RANDOM_SEED = 20260519


def _summary(values: list[float]) -> dict[str, float | int]:
    return {
        "min": min(values),
        "mean": mean(values),
        "median": median(values),
        "max": max(values),
        "stddev": pstdev(values) if len(values) > 1 else 0.0,
    }


def _json_loads_body(body: bytes) -> dict[str, Any]:
    return json.loads(body.decode("utf-8") or "{}")


def _extract_rpc_name(body: dict[str, Any]) -> str:
    if "name" in body:
        return str(body["name"])
    result = body.get("result")
    if isinstance(result, dict):
        if "name" in result:
            return str(result["name"])
        nested_result = result.get("result")
        if isinstance(nested_result, dict) and "name" in nested_result:
            return str(nested_result["name"])
        params = result.get("params")
        if isinstance(params, dict) and "name" in params:
            return str(params["name"])
        data = result.get("data")
        if isinstance(data, dict) and "name" in data:
            return str(data["name"])
    raise AssertionError(f"could not extract RPC name from {body!r}")


def create_tigrbl_rest_transport_app(_: Path) -> TigrblApp:
    app = TigrblApp(title="Tigrbl REST Transport Benchmark")

    async def create_item(request: TigrblRequest) -> dict[str, Any]:
        payload = _json_loads_body(request.body)
        return {"id": payload.get("id", 0), "name": str(payload["name"])}

    app.add_route("/items", create_item, methods=["POST"])
    return app


def create_fastapi_rest_transport_app(_: Path) -> FastAPI:
    app = FastAPI()

    @app.post("/items")
    async def create_item(request: FastAPIRequest) -> dict[str, Any]:
        payload = await request.json()
        return {"id": payload.get("id", 0), "name": str(payload["name"])}

    return app


def create_tigrbl_rpc_transport_app(_: Path) -> TigrblApp:
    app = TigrblApp(title="Tigrbl RPC Transport Benchmark")

    async def rpc(request: TigrblRequest) -> dict[str, Any]:
        payload = _json_loads_body(request.body)
        params = dict(payload.get("params") or {})
        return {
            "jsonrpc": "2.0",
            "result": {"id": params.get("id", 0), "name": str(params["name"])},
            "id": payload.get("id"),
        }

    app.add_route("/rpc", rpc, methods=["POST"])
    return app


def _ensure_rpc_items_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS benchmark_item "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        conn.commit()


def _fetch_rpc_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM benchmark_item ORDER BY id").fetchall()
    return [str(row[0]) for row in rows]


def create_fastapi_rpc_transport_app(_: Path) -> FastAPI:
    app = FastAPI()

    @app.post("/rpc")
    async def rpc(request: FastAPIRequest) -> dict[str, Any]:
        payload = await request.json()
        params = dict(payload.get("params") or {})
        return {
            "jsonrpc": "2.0",
            "result": {"id": params.get("id", 0), "name": str(params["name"])},
            "id": payload.get("id"),
        }

    return app


def create_fastapi_rpc_db_app(db_path: Path) -> FastAPI:
    _ensure_rpc_items_db(db_path)
    app = FastAPI()

    @app.post("/rpc")
    async def rpc(request: FastAPIRequest) -> dict[str, Any]:
        payload = await request.json()
        params = dict(payload.get("params") or {})
        name = str(params["name"])
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("INSERT INTO benchmark_item(name) VALUES(?)", (name,))
            conn.commit()
            item_id = int(cursor.lastrowid or 0)
        return {
            "jsonrpc": "2.0",
            "result": {"id": item_id, "name": name},
            "id": payload.get("id"),
        }

    return app


async def _initialize_none(_: Any) -> None:
    return None


async def _dispose_none(_: Any) -> None:
    return None


async def _initialize_tigrbl_ws_or_stream(app: Any) -> None:
    if hasattr(app, "engine"):
        try:
            await initialize_tigrbl_websocket_app(app)
        except ValueError as exc:
            if "Engine provider is not configured" not in str(exc):
                raise


async def _dispose_tigrbl_ws_or_stream(app: Any) -> None:
    if hasattr(app, "engine"):
        try:
            await dispose_tigrbl_websocket_app(app)
        except ValueError as exc:
            if "Engine provider is not configured" not in str(exc):
                raise


async def _bench_http_post(
    *,
    create_app: Callable[[Path], Any],
    initialize: Callable[[Any], Awaitable[None]],
    dispose: Callable[[Any], Awaitable[None]],
    endpoint: str,
    payload_for: Callable[[int, str], dict[str, Any]],
    extract_name: Callable[[dict[str, Any]], str],
    fetch_names: Callable[[Path], list[str]] | None,
    runner: str,
    ops: int,
    label: str,
) -> dict[str, Any]:
    with TemporaryDirectory(dir=TMP_ROOT, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / f"{label}.sqlite3"
        app = create_app(db_path)
        await initialize(app)
        server: Any = None
        task: Any = None
        try:
            if runner == "uvicorn":
                base_url, server, task = await run_uvicorn_in_task(app)
                client_kwargs = {"base_url": base_url, "timeout": 20.0}
                runner_name = "httpx.AsyncClient over uvicorn real HTTP transport"
            elif runner == "asgitransport":
                client_kwargs = {
                    "transport": httpx.ASGITransport(app=app),
                    "base_url": "http://testserver",
                    "timeout": 20.0,
                }
                runner_name = "httpx.ASGITransport"
            else:
                raise ValueError(f"unknown http runner: {runner}")

            async with httpx.AsyncClient(**client_kwargs) as client:
                for idx in range(WARMUP_OPS):
                    name = f"warmup-{label}-{idx}"
                    response = await client.post(endpoint, json=payload_for(idx, name))
                    assert response.status_code in {200, 201}, response.text
                    assert extract_name(response.json()) == name

                measured_names = [f"{label}-{idx}" for idx in range(ops)]
                start = perf_counter()
                for idx, name in enumerate(measured_names):
                    response = await client.post(endpoint, json=payload_for(idx, name))
                    assert response.status_code in {200, 201}, response.text
                    assert extract_name(response.json()) == name
                elapsed = perf_counter() - start

            if fetch_names is not None:
                persisted = fetch_names(db_path)
                assert persisted[-ops:] == measured_names
        finally:
            if server is not None and task is not None:
                await stop_uvicorn_server(server, task)
            await dispose(app)

    return {
        "ops": ops,
        "total_seconds": elapsed,
        "ops_per_second": ops / elapsed,
        "runner": runner_name,
    }


async def _read_stream_bytes(client: httpx.AsyncClient, endpoint: str) -> bytes:
    async with client.stream("GET", endpoint) as response:
        assert response.status_code == 200, await response.aread()
        payload = bytearray()
        async for chunk in response.aiter_bytes():
            payload.extend(chunk)
    return bytes(payload)


async def _bench_stream(
    *,
    create_app: Callable[[Path], Any],
    initialize: Callable[[Any], Awaitable[None]],
    dispose: Callable[[Any], Awaitable[None]],
    endpoint: str,
    expected_body: bytes,
    ops: int,
    label: str,
) -> dict[str, Any]:
    with TemporaryDirectory(dir=TMP_ROOT, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / f"{label}.sqlite3"
        app = create_app(db_path)
        await initialize(app)
        try:
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://testserver",
                timeout=20.0,
            ) as client:
                for _ in range(WARMUP_OPS):
                    assert await _read_stream_bytes(client, endpoint) == expected_body
                start = perf_counter()
                for _ in range(ops):
                    assert await _read_stream_bytes(client, endpoint) == expected_body
                elapsed = perf_counter() - start
        finally:
            await dispose(app)
    return {
        "ops": ops,
        "total_seconds": elapsed,
        "ops_per_second": ops / elapsed,
        "bytes_per_response": len(expected_body),
        "runner": "httpx.ASGITransport stream reader",
    }


async def _run_websocket_session(app: Any, *, path: str, text: str) -> str:
    sent: list[dict[str, Any]] = []
    pending = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": text},
    ]

    async def receive() -> dict[str, Any]:
        return pending.pop(0) if pending else {"type": "websocket.disconnect", "code": 1000}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(
        {
            "type": "websocket",
            "scheme": "ws",
            "path": path,
            "query_string": b"",
            "headers": [],
            "subprotocols": [],
        },
        receive,
        send,
    )
    for message in sent:
        if message.get("type") != "websocket.send":
            continue
        text_payload = message.get("text")
        if isinstance(text_payload, str):
            return text_payload
        bytes_payload = message.get("bytes")
        if isinstance(bytes_payload, (bytes, bytearray)):
            return bytes(bytes_payload).decode("utf-8")
    raise AssertionError(f"no websocket.send payload found in {sent!r}")


async def _bench_websocket(
    *,
    create_app: Callable[[Path], Any],
    initialize: Callable[[Any], Awaitable[None]],
    dispose: Callable[[Any], Awaitable[None]],
    endpoint: str,
    db_bound: bool,
    ops: int,
    label: str,
) -> dict[str, Any]:
    with TemporaryDirectory(dir=TMP_ROOT, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / f"{label}.sqlite3"
        app = create_app(db_path)
        await initialize(app)
        measured_names: list[str] = []
        try:
            if db_bound:
                for idx in range(WARMUP_OPS):
                    name = f"warmup-{label}-{idx}"
                    text = await _run_websocket_session(
                        app,
                        path=endpoint,
                        text=json.dumps({"name": name}, separators=(",", ":")),
                    )
                    assert json.loads(text)["name"] == name
                start = perf_counter()
                for idx in range(ops):
                    name = f"{label}-{idx}"
                    text = await _run_websocket_session(
                        app,
                        path=endpoint,
                        text=json.dumps({"name": name}, separators=(",", ":")),
                    )
                    assert json.loads(text)["name"] == name
                    measured_names.append(name)
                elapsed = perf_counter() - start
                assert fetch_websocket_names(db_path)[-ops:] == measured_names
            else:
                for idx in range(WARMUP_OPS):
                    text = f"warmup-{label}-{idx}"
                    assert await _run_websocket_session(app, path=endpoint, text=text) == text
                start = perf_counter()
                for idx in range(ops):
                    text = f"{label}-{idx}"
                    assert await _run_websocket_session(app, path=endpoint, text=text) == text
                elapsed = perf_counter() - start
        finally:
            await dispose(app)
    return {
        "ops": ops,
        "total_seconds": elapsed,
        "ops_per_second": ops / elapsed,
        "runner": "direct ASGI websocket session",
    }


def _case_definitions() -> list[dict[str, Any]]:
    rest_payload = lambda idx, name: {"name": name}
    rest_extract = lambda body: str(body["name"])
    rpc_payload = lambda idx, name: {
        "jsonrpc": "2.0",
        "method": tigrbl_create_rpc_method(),
        "params": {"name": name},
        "id": idx + 1,
    }
    rpc_extract = _extract_rpc_name
    return [
        {
            "surface": "rest",
            "mode": "transport_only",
            "kind": "http",
            "runner": "asgitransport",
            "endpoint": "/items",
            "payload_for": rest_payload,
            "extract_name": rest_extract,
            "tigrbl": (create_tigrbl_rest_transport_app, _initialize_none, _dispose_none, None),
            "fastapi": (create_fastapi_rest_transport_app, _initialize_none, _dispose_none, None),
        },
        {
            "surface": "rest",
            "mode": "db_bound",
            "kind": "http",
            "runner": "uvicorn",
            "endpoint": tigrbl_create_path(),
            "payload_for": rest_payload,
            "extract_name": rest_extract,
            "tigrbl": (create_tigrbl_app, initialize_tigrbl_app, dispose_tigrbl_app, fetch_tigrbl_names),
            "fastapi": (create_fastapi_app, _initialize_none, dispose_fastapi_app, fetch_fastapi_names),
        },
        {
            "surface": "rpc",
            "mode": "transport_only",
            "kind": "http",
            "runner": "asgitransport",
            "endpoint": "/rpc",
            "payload_for": rpc_payload,
            "extract_name": rpc_extract,
            "tigrbl": (create_tigrbl_rpc_transport_app, _initialize_none, _dispose_none, None),
            "fastapi": (create_fastapi_rpc_transport_app, _initialize_none, _dispose_none, None),
        },
        {
            "surface": "rpc",
            "mode": "db_bound",
            "kind": "http",
            "runner": "uvicorn",
            "endpoint": "/rpc",
            "payload_for": rpc_payload,
            "extract_name": rpc_extract,
            "tigrbl": (create_tigrbl_app, initialize_tigrbl_app, dispose_tigrbl_app, fetch_tigrbl_names),
            "fastapi": (create_fastapi_rpc_db_app, _initialize_none, _dispose_none, _fetch_rpc_names),
        },
        {
            "surface": "websocket",
            "mode": "transport_only",
            "kind": "websocket",
            "endpoint": "/ws/echo",
            "db_bound": False,
            "tigrbl": (create_tigrbl_websocket_transport_app, _initialize_tigrbl_ws_or_stream, _dispose_tigrbl_ws_or_stream),
            "fastapi": (create_fastapi_websocket_transport_app, _initialize_none, _dispose_none),
        },
        {
            "surface": "websocket",
            "mode": "db_bound",
            "kind": "websocket",
            "endpoint": "/ws/items",
            "db_bound": True,
            "tigrbl": (create_tigrbl_websocket_db_app, _initialize_tigrbl_ws_or_stream, _dispose_tigrbl_ws_or_stream),
            "fastapi": (create_fastapi_websocket_db_app, _initialize_none, _dispose_none),
        },
        {
            "surface": "stream",
            "mode": "transport_only",
            "kind": "stream",
            "endpoint": "/stream/fixed",
            "expected_body": expected_transport_stream_bytes(),
            "tigrbl": (create_tigrbl_streaming_transport_app, _initialize_tigrbl_ws_or_stream, _dispose_tigrbl_ws_or_stream),
            "fastapi": (create_fastapi_streaming_transport_app, _initialize_none, _dispose_none),
        },
        {
            "surface": "stream",
            "mode": "db_bound",
            "kind": "stream",
            "endpoint": "/stream/items",
            "expected_body": expected_db_stream_bytes(),
            "tigrbl": (create_tigrbl_streaming_db_app, _initialize_tigrbl_ws_or_stream, _dispose_tigrbl_ws_or_stream),
            "fastapi": (create_fastapi_streaming_db_app, _initialize_none, _dispose_none),
        },
    ]


async def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(f"{RANDOM_SEED}:{case['surface']}:{case['mode']}")
    rounds: list[dict[str, Any]] = []
    per_framework: dict[str, list[float]] = {"tigrbl": [], "fastapi": []}

    for round_index in range(1, ROUNDS + 1):
        order = ["tigrbl", "fastapi"]
        rng.shuffle(order)
        round_results: dict[str, Any] = {}
        for framework in order:
            label = f"{case['surface']}-{case['mode']}-{framework}-r{round_index}"
            definition = case[framework]
            if case["kind"] == "http":
                create_app, initialize, dispose, fetch_names = definition
                result = await _bench_http_post(
                    create_app=create_app,
                    initialize=initialize,
                    dispose=dispose,
                    endpoint=case["endpoint"],
                    payload_for=case["payload_for"],
                    extract_name=case["extract_name"],
                    fetch_names=fetch_names,
                    runner=case["runner"],
                    ops=OPS,
                    label=label,
                )
            elif case["kind"] == "websocket":
                create_app, initialize, dispose = definition
                result = await _bench_websocket(
                    create_app=create_app,
                    initialize=initialize,
                    dispose=dispose,
                    endpoint=case["endpoint"],
                    db_bound=bool(case["db_bound"]),
                    ops=OPS,
                    label=label,
                )
            elif case["kind"] == "stream":
                create_app, initialize, dispose = definition
                result = await _bench_stream(
                    create_app=create_app,
                    initialize=initialize,
                    dispose=dispose,
                    endpoint=case["endpoint"],
                    expected_body=case["expected_body"],
                    ops=OPS,
                    label=label,
                )
            else:
                raise ValueError(case["kind"])
            round_results[framework] = result
            per_framework[framework].append(float(result["ops_per_second"]))

        tigrbl_ops = float(round_results["tigrbl"]["ops_per_second"])
        fastapi_ops = float(round_results["fastapi"]["ops_per_second"])
        rounds.append(
            {
                "round": round_index,
                "order": order,
                "results": round_results,
                "delta_ops_per_second_tigrbl_minus_fastapi": tigrbl_ops - fastapi_ops,
                "throughput_ratio_tigrbl_over_fastapi": tigrbl_ops / fastapi_ops if fastapi_ops else 0.0,
            }
        )
        print(
            f"{case['surface']}/{case['mode']} round {round_index:02d}: "
            f"tigrbl={tigrbl_ops:.3f} fastapi={fastapi_ops:.3f} "
            f"delta={tigrbl_ops - fastapi_ops:.3f}",
            flush=True,
        )

    tigrbl_mean = mean(per_framework["tigrbl"])
    fastapi_mean = mean(per_framework["fastapi"])
    return {
        "surface": case["surface"],
        "mode": case["mode"],
        "ops_per_round": OPS,
        "round_count": ROUNDS,
        "warmup_ops": WARMUP_OPS,
        "endpoint": case["endpoint"],
        "rounds": rounds,
        "summary": {
            "tigrbl": _summary(per_framework["tigrbl"]),
            "fastapi": _summary(per_framework["fastapi"]),
            "delta_ops_per_second_tigrbl_minus_fastapi": tigrbl_mean - fastapi_mean,
            "throughput_ratio_tigrbl_over_fastapi": tigrbl_mean / fastapi_mean if fastapi_mean else 0.0,
        },
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    rows = [
        "| Surface | Mode | Tigrbl mean ops/s | FastAPI mean ops/s | Delta ops/s | Ratio |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for case in payload["cases"]:
        summary = case["summary"]
        rows.append(
            "| {surface} | {mode} | {tigrbl:.3f} | {fastapi:.3f} | {delta:.3f} | {ratio:.3f}x |".format(
                surface=case["surface"],
                mode=case["mode"],
                tigrbl=summary["tigrbl"]["mean"],
                fastapi=summary["fastapi"]["mean"],
                delta=summary["delta_ops_per_second_tigrbl_minus_fastapi"],
                ratio=summary["throughput_ratio_tigrbl_over_fastapi"],
            )
        )
    return (
        "# Tigrbl vs FastAPI Surface Matrix Benchmark\n\n"
        f"- rounds: {payload['round_count']}\n"
        f"- measured operations per framework per round: {payload['ops_per_round']}\n"
        f"- warmup operations per framework per round: {payload['warmup_ops']}\n"
        f"- random seed: {payload['random_seed']}\n"
        f"- generated artifact: `{OUT_JSON}`\n\n"
        + "\n".join(rows)
        + "\n"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the reusable Tigrbl vs FastAPI 25x250 surface matrix benchmark "
            "across REST, JSON-RPC, websocket, and stream transport modes."
        )
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=DEFAULT_ROUNDS,
        help=f"Measured rounds per surface/mode. Default: {DEFAULT_ROUNDS}.",
    )
    parser.add_argument(
        "--ops",
        type=int,
        default=DEFAULT_OPS,
        help=f"Measured operations per framework per round. Default: {DEFAULT_OPS}.",
    )
    parser.add_argument(
        "--warmup-ops",
        type=int,
        default=DEFAULT_WARMUP_OPS,
        help=f"Warmup operations per framework per round. Default: {DEFAULT_WARMUP_OPS}.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help=f"Randomization seed for per-round framework order. Default: {RANDOM_SEED}.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=DEFAULT_JSON_OUTPUT,
        help=f"JSON output path. Default: {DEFAULT_JSON_OUTPUT}.",
    )
    parser.add_argument(
        "--md-output",
        type=Path,
        default=DEFAULT_MD_OUTPUT,
        help=f"Markdown output path. Default: {DEFAULT_MD_OUTPUT}.",
    )
    parser.add_argument(
        "--tmp-root",
        type=Path,
        default=DEFAULT_TMP_ROOT,
        help=f"Temporary workspace root. Default: {DEFAULT_TMP_ROOT}.",
    )
    return parser.parse_args(argv)


async def main(argv: list[str] | None = None) -> None:
    global OPS, OUT_JSON, OUT_MD, RANDOM_SEED, ROUNDS, TMP_ROOT, WARMUP_OPS

    args = parse_args(argv)
    ROUNDS = args.rounds
    OPS = args.ops
    WARMUP_OPS = args.warmup_ops
    RANDOM_SEED = args.seed
    OUT_JSON = args.json_output
    OUT_MD = args.md_output
    TMP_ROOT = args.tmp_root

    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, Any]] = []
    for case in _case_definitions():
        cases.append(await _run_case(case))

    payload = {
        "benchmark": "tigrbl-vs-fastapi-surface-matrix",
        "round_count": ROUNDS,
        "ops_per_round": OPS,
        "warmup_ops": WARMUP_OPS,
        "random_seed": RANDOM_SEED,
        "json_output": str(OUT_JSON),
        "md_output": str(OUT_MD),
        "cases": cases,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(_render_markdown(payload), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    asyncio.run(main())
