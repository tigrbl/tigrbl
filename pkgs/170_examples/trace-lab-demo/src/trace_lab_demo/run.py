"""Serve the trace lab or run its real-network smoke scenario and exit."""

import argparse
import asyncio
import importlib.util
import inspect
import json
import os
import struct
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from .capture import Capture
from .gateway import build_gateway
from trace_lab.http import reply

HERE = Path(__file__).resolve().parent
ORIGIN = "https://localhost:8088"


def load_probe(tigrcorn):
    path = tigrcorn / "tests/fixtures_third_party/wt_stream_client.py"
    spec = importlib.util.spec_from_file_location("trace_lab_wt_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.probe_wt_stream


async def exercise(base_url, quic_port, certificate, probe, note_id):
    import httpx
    from websockets.asyncio.client import connect

    topic = f"trace-lab:{note_id}"
    async with httpx.AsyncClient(
        base_url=base_url, timeout=6, trust_env=False
    ) as client:
        rest = await client.post("/notes", json={"id": note_id, "name": "Trace lab"})
        rest.raise_for_status()
        rpc = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": "read",
                "method": "Note.read",
                "params": {"id": note_id},
            },
        )
        rpc.raise_for_status()
        assert rpc.json().get("result", {}).get("id") == note_id, rpc.text
        assert rest.headers["x-correlation-id"] != rpc.headers["x-correlation-id"]

    async with connect(
        base_url.replace("http:", "ws:", 1) + "/ws/activity",
        subprotocols=["jsonrpc"],
        proxy=None,
    ) as subscriber:

        async def call(socket, method, params, request_id):
            await socket.send(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": method,
                        "params": params,
                    }
                )
            )
            reply = json.loads(await asyncio.wait_for(socket.recv(), 5))
            assert reply.get("id") == request_id and "result" in reply, reply
            return reply["result"]

        subscribed = await call(
            subscriber, "Activity.subscribe", {"channel": topic}, "subscribe"
        )
        assert subscribed.get("subscribed") and subscribed.get(
            "transport_session_id"
        ), subscribed
        async with connect(
            base_url.replace("http:", "ws:", 1) + "/ws/activity",
            subprotocols=["jsonrpc"],
            proxy=None,
        ) as publisher:
            published = await call(
                publisher,
                "Activity.publish",
                {"channel": topic, "event": {"note_id": note_id}},
                "publish",
            )
            notification = json.loads(await asyncio.wait_for(subscriber.recv(), 5))
            assert (
                notification["params"]["publication_id"] == published["publication_id"]
            )

    request = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": "wt-echo",
            "method": "Trace.echo",
            "params": {},
        }
    ).encode()
    wt = await probe(
        "127.0.0.1",
        quic_port,
        trusted_certificates=[certificate],
        local_cid=uuid4().bytes[:8],
        second_session=True,
        rebind_before_second_session=True,
        payload=struct.pack("!I", len(request)) + request,
        datagram_payload=b"hello-datagram",
        wait_for_datagram_response=False,
        close_connection=True,
    )
    assert wt.status == 200, wt.to_jsonable()
    body = wt.stream_bodies[wt.stream_id]
    if len(body) >= 4 and struct.unpack("!I", body[:4])[0] == len(body) - 4:
        body = body[4:]
    echo = json.loads(body)
    assert (
        echo.get("id") == "wt-echo" and echo.get("result", {}).get("accepted") is True
    ), echo
    return {
        "rest": str(rest.status_code),
        "http_jsonrpc": str(rpc.status_code),
        "websocket": "delivery received",
        "webtransport": "two QUIC sessions",
    }


async def serve(args):
    from tigrbl import Timeline, resolver
    from tigrcorn.config.load import build_config
    from tigrcorn.server.runner import TigrCornServer
    from tigrcorn.transports.quic.handshake import generate_self_signed_certificate

    from .trace_app import build_app

    timeline = Timeline()
    capture = Capture(timeline)
    certificate, key = generate_self_signed_certificate("server.example")
    async with AsyncExitStack() as stack:
        scratch = Path(stack.enter_context(TemporaryDirectory(prefix="tigrbl-trace-")))
        certfile, keyfile = scratch / "cert.pem", scratch / "key.pem"
        certfile.write_bytes(certificate)
        keyfile.write_bytes(key)
        exporter = None
        if collector_url := os.environ.get("TRACE_COLLECTOR_URL"):
            from tigrbl_trace_transport import TraceExporter

            exporter = TraceExporter(
                collector_url,
                os.environ["TRACE_INGEST_TOKEN"],
                os.environ.get("TRACE_SERVICE", "trace-lab-primary"),
                os.environ.get("TRACE_ENVIRONMENT", "local"),
            )
            exporter.start()
            stack.push_async_callback(exporter.close)
        app = build_app(scratch / "trace.sqlite3", capture, exporter)
        initialized = app.initialize()
        if inspect.isawaitable(initialized):
            await initialized
        engine, _ = resolver.resolve_provider().ensure()
        stack.callback(engine.dispose)
        stack.push_async_callback(app.realtime_broker.close)
        probe = load_probe(args.tigrcorn_source)

        async def run_scenario(note_id):
            return await exercise(base_url, quic_port, certificate, probe, note_id)

        gateway = build_gateway(
            app, capture, args.frontend, run_scenario, reply, lambda: base_url
        )

        tcp = TigrCornServer(
            gateway,
            build_config(
                host="127.0.0.1",
                port=args.port,
                lifespan="off",
                http_versions=["1.1"],
                protocols=["http1", "websocket"],
            ),
        )
        udp = TigrCornServer(
            gateway,
            build_config(
                transport="udp",
                host="127.0.0.1",
                port=args.quic_port,
                lifespan="off",
                http_versions=["3"],
                protocols=["webtransport"],
                ssl_certfile=str(certfile),
                ssl_keyfile=str(keyfile),
                webtransport_path="/wt",
                webtransport_origins=[ORIGIN],
                webtransport_max_sessions=2,
            ),
        )
        for server in (tcp, udp):
            await server.start()
            stack.push_async_callback(server.close)
        port = tcp._listeners[0].server.sockets[0].getsockname()[1]
        quic_port = udp._listeners[0].transport.get_extra_info("sockname")[1]
        base_url = f"http://127.0.0.1:{port}"
        print(f"Trace Lab {base_url} (QUIC UDP {quic_port})", flush=True)

        if args.smoke:
            await smoke(base_url)
        else:
            await asyncio.Event().wait()


async def smoke(base_url):
    import httpx

    async with httpx.AsyncClient(
        base_url=base_url, timeout=30, trust_env=False
    ) as client:
        page = await client.get("/")
        assert "Transport Trace Lab" in page.text
        run = await client.post("/demo/run")
        assert run.is_success, run.text
        payload = (await client.get("/demo/trace")).json()
    rows = payload["events"]
    assert {row["transport"] for row in rows} >= {
        "rest",
        "http_jsonrpc",
        "websocket",
        "webtransport",
        "database",
    }
    assert run.json()["status"] == "completed"
    assert payload["last_run_summary"] == run.json()
    for key in (
        "connection_id",
        "transport_session_id",
        "stream_correlation_id",
        "datagram_id",
        "subscription_id",
        "invocation_id",
        "transaction_id",
    ):
        assert any(row.get(key) is not None for row in rows), (
            f"No {key} in the live trace"
        )
    streams = [row for row in rows if row["kind"] == "wt.stream.received"]
    assert len({row["connection_id"] for row in streams}) == 1, streams
    assert len({row["transport_session_id"] for row in streams}) == 2, streams
    assert len({row["correlation_id"] for row in streams}) == 2, streams
    assert all(row.get("stream_correlation_id") for row in streams)
    assert any(
        row.get("rpc_id") == "wt-echo" and row["kind"] == "invocation.completed"
        for row in rows
    )
    assert any(row["outcome"] == "delivered" and row.get("delivery_id") for row in rows)
    assert any(
        row["kind"] == "db.tx.commit" and row.get("invocation_id") for row in rows
    )
    assert await verify_static(base_url)
    print(
        f"Smoke passed: {len(rows)} events, {payload['rollup']['transactions']} transactions",
        flush=True,
    )


async def verify_static(base_url):
    import re

    import httpx

    async with httpx.AsyncClient(base_url=base_url, trust_env=False) as client:
        document = await client.get("/distributions")
        assert document.status_code == 200
        favicon = await client.get("/favicon.svg")
        assert favicon.is_success and favicon.headers["content-type"].startswith(
            "image/svg+xml"
        )
        asset = re.search(r'src="(/assets/[^"]+)"', document.text)
        assert asset, "No bundled JavaScript asset in the document"
        assert (await client.get(asset[1])).is_success
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    workspace = HERE.parents[4]
    sources = workspace / ".sources/trace-lab"
    parser.add_argument("--tigrcorn-source", type=Path, default=sources / "tigrcorn")
    parser.add_argument(
        "--contract-source", type=Path, default=sources / "tigr-asgi-contract"
    )
    parser.add_argument(
        "--frontend",
        type=Path,
        default=workspace / "pkgs/130_frontend/trace-lab-ui/dist",
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--quic-port", type=int, default=0)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if not (args.frontend / "index.html").is_file():
        parser.error("Build the frontend and supply its bundle with --frontend.")
    if not args.tigrcorn_source.is_dir():
        parser.error("Provide the Tigrcorn checkout used for the WebTransport probe.")
    if os.environ.get("TRACE_COLLECTOR_URL") and not os.environ.get(
        "TRACE_INGEST_TOKEN"
    ):
        parser.error("TRACE_INGEST_TOKEN is required with TRACE_COLLECTOR_URL")
    source_dirs = [
        args.tigrcorn_source / "src",
        *(pkg / "src" for pkg in sorted((args.tigrcorn_source / "pkgs").iterdir())),
        args.contract_source / "packages/contract-py/src",
    ]
    sys.path[:0] = [str(path) for path in source_dirs if path.is_dir()]
    try:
        asyncio.run(serve(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
