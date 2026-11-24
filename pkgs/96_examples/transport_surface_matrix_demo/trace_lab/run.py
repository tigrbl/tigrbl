"""Serve the trace lab or run its real-network smoke scenario and exit."""

import argparse
import asyncio
from contextlib import AsyncExitStack
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import struct
from tempfile import TemporaryDirectory
from uuid import uuid4


HERE = Path(__file__).resolve().parent
ORIGIN = "https://localhost:8088"


def source_paths(tigrbl, tigrcorn, contract):
    """Select explicit source checkouts before importing the demo dependencies."""
    framework = [
        pkg / "src" if (pkg / "src").is_dir() else pkg
        for pkg in sorted((tigrbl / "pkgs").glob("*/*"))
        if (pkg / "pyproject.toml").is_file() and pkg.parent.name < "96_examples"
    ]
    server = [
        tigrcorn / "src",
        *(pkg / "src" for pkg in sorted((tigrcorn / "pkgs").iterdir())),
    ]
    sys.path[:0] = [
        str(path)
        for path in [*framework, *server, contract / "packages/contract-py/src"]
        if path.is_dir()
    ]


def load_probe(tigrcorn):
    path = tigrcorn / "tests/fixtures_third_party/wt_stream_client.py"
    spec = importlib.util.spec_from_file_location("trace_lab_wt_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.probe_wt_stream


async def exercise(base_url, quic_port, certificate, probe):
    import httpx
    from websockets.asyncio.client import connect

    note_id = uuid4().hex
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
        "REST": rest.status_code,
        "JSON-RPC": rpc.status_code,
        "WebSocket": "delivery received",
        "WebTransport": "two QUIC sessions",
    }


async def reply(send, status, payload, content_type="application/json"):
    if content_type == "application/json":
        payload = json.dumps(payload, separators=(",", ":")).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", content_type.encode()),
                (b"cache-control", b"no-store"),
                (b"x-content-type-options", b"nosniff"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": payload})


async def serve(args):
    from trace_app import build_app
    from tigrbl import Timeline, resolver
    from tigrcorn.config.load import build_config
    from tigrcorn.server.runner import TigrCornServer
    from tigrcorn.transports.quic.handshake import generate_self_signed_certificate

    timeline = Timeline()
    lock = asyncio.Lock()
    certificate, key = generate_self_signed_certificate("server.example")
    async with AsyncExitStack() as stack:
        scratch = Path(stack.enter_context(TemporaryDirectory(prefix="tigrbl-trace-")))
        certfile, keyfile = scratch / "cert.pem", scratch / "key.pem"
        certfile.write_bytes(certificate)
        keyfile.write_bytes(key)
        app = build_app(scratch / "trace.sqlite3", timeline)
        initialized = app.initialize()
        if inspect.isawaitable(initialized):
            await initialized
        engine, _ = resolver.resolve_provider().ensure()
        stack.callback(engine.dispose)
        stack.push_async_callback(app.realtime_broker.close)
        probe = load_probe(args.tigrcorn_source)
        dashboard = (HERE / "index.html").read_bytes()

        async def gateway(scope, receive, send):
            path, transport = scope.get("path"), scope["type"]
            if transport == "http" and path in {"/", "/demo/trace", "/demo/run"}:
                if path == "/" and scope["method"] == "GET":
                    return await reply(send, 200, dashboard, "text/html; charset=utf-8")
                if path == "/demo/trace" and scope["method"] == "GET":
                    return await reply(send, 200, timeline.data())
                if path == "/demo/run" and scope["method"] == "POST":
                    host = dict(scope["headers"]).get(b"host")
                    origin = dict(scope["headers"]).get(b"origin")
                    if host != f"127.0.0.1:{port}".encode() or origin not in (
                        None,
                        base_url.encode(),
                    ):
                        return await reply(
                            send, 403, {"error": "Use the displayed loopback URL."}
                        )
                    if lock.locked():
                        return await reply(
                            send, 409, {"error": "A scenario is already running."}
                        )
                    async with lock:
                        try:
                            results = await asyncio.wait_for(
                                exercise(base_url, quic_port, certificate, probe), 25
                            )
                        except Exception as exc:
                            timeline.add(
                                "Scenario failed",
                                "Lab",
                                {"outcome": type(exc).__name__},
                            )
                            print(f"Scenario failed: {exc}", file=sys.stderr)
                            return await reply(send, 500, {"error": str(exc)})
                    return await reply(send, 200, results)
                return await reply(send, 405, {"error": "Method not supported."})
            await app(scope, receive, send)

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
    trace = payload["rollup"]
    rows = payload["events"]
    assert {row["transport"] for row in rows} >= {
        "REST",
        "JSON-RPC",
        "WebSocket",
        "WebTransport",
    }
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
    streams = [row for row in rows if row["kind"] == "webtransport.stream.receive"]
    assert len({row["connection_id"] for row in streams}) == 1, streams
    assert len({row["transport_session_id"] for row in streams}) == 2, streams
    assert len({row["correlation_id"] for row in streams}) == 2, streams
    assert all(row.get("stream_correlation_id") for row in streams)
    assert any(
        row.get("rpc_id") == "wt-echo" and row.get("outcome") == "dispatch"
        for row in rows
    )
    assert any(row["outcome"] == "delivered" for row in trace["deliveries"].values())
    assert any(
        "committed" in tx["outcomes"] and tx["invocations"]
        for tx in trace["transactions"]
    )
    print(
        f"Smoke passed: {len(rows)} events, {len(trace['transactions'])} transactions",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = HERE.parents[3]
    parser.add_argument("--tigrbl-source", type=Path, default=default)
    parser.add_argument(
        "--tigrcorn-source", type=Path, default=default.parent / "tigrcorn"
    )
    parser.add_argument(
        "--contract-source", type=Path, default=default.parent / "tigr-asgi-contract"
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--quic-port", type=int, default=0)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    for root in (args.tigrbl_source, args.tigrcorn_source, args.contract_source):
        if not root.is_dir():
            parser.error(f"Source checkout not found: {root}")
    source_paths(args.tigrbl_source, args.tigrcorn_source, args.contract_source)
    try:
        asyncio.run(serve(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
