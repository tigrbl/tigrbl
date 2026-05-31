from __future__ import annotations

import asyncio
import importlib.util
import json
import ssl
import sys
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
TIGRCORN_ROOT = ROOT.parent / "tigrcorn"
for src_dir in sorted((TIGRCORN_ROOT / "pkgs").glob("*/src")):
    sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(TIGRCORN_ROOT / "src"))
sys.path.insert(0, str(TIGRCORN_ROOT))

from tests.fixtures_third_party.h11_http1_client import probe_http11  # noqa: E402
from tests.fixtures_third_party.h11_stream_client import probe_h11_stream  # noqa: E402
from tests.fixtures_third_party.h2_http2_client import probe_h2c  # noqa: E402
from tests.fixtures_third_party.h3_http3_client import probe_h3  # noqa: E402
from tests.fixtures_third_party.ws_wss_client import probe_ws_wss  # noqa: E402
from tests.fixtures_third_party.wt_stream_client import probe_wt_stream  # noqa: E402
from tigrcorn.config.load import build_config  # noqa: E402
from tigrcorn.server.runner import TigrCornServer  # noqa: E402
from tigrcorn.transports.quic.handshake import generate_self_signed_certificate  # noqa: E402


CERTS = TIGRCORN_ROOT / "tests" / "fixtures_certs"
SERVER_CERT = CERTS / "interop-localhost-cert.pem"
SERVER_KEY = CERTS / "interop-localhost-key.pem"
APP_PATH = ROOT / "examples" / "transport_demo" / "app.py"


def build_app() -> Any:
    spec = importlib.util.spec_from_file_location("transport_demo_app", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load transport demo app from {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_app()


def build_fail_closed_examples() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("transport_demo_app", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load transport demo app from {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_fail_closed_examples()


async def _start_server(*, app: Any, config: Any) -> tuple[TigrCornServer, int]:
    server = TigrCornServer(app, config)
    await server.start()
    listener = server._listeners[0]
    if hasattr(listener, "transport"):
        port = listener.transport.get_extra_info("sockname")[1]
    else:
        port = listener.server.sockets[0].getsockname()[1]
    return server, int(port)


async def _safe_close(server: TigrCornServer, timeout: float = 1.0) -> None:
    with suppress(Exception):
        await asyncio.wait_for(server.close(), timeout=timeout)


def _ok(label: str, payload: Any) -> dict[str, Any]:
    return {"demo": label, "ok": True, "payload": payload}


def _err(label: str, exc: Exception) -> dict[str, Any]:
    return {"demo": label, "ok": False, "error": type(exc).__name__, "message": str(exc)}


async def _http11_rest() -> dict[str, Any]:
    app = build_app()
    config = build_config(host="127.0.0.1", port=0, lifespan="off", http_versions=["1.1"])
    server, port = await _start_server(app=app, config=config)
    try:
        response = await probe_http11(
            "127.0.0.1",
            port,
            method="POST",
            target="/items",
            headers=[("content-type", "application/json")],
            body=b'{"name":"Ada-h11"}',
        )
        return _ok("h11-rest", response.to_jsonable())
    except Exception as exc:
        return _err("h11-rest", exc)
    finally:
        await _safe_close(server)


async def _http11_jsonrpc() -> dict[str, Any]:
    app = build_app()
    config = build_config(host="127.0.0.1", port=0, lifespan="off", http_versions=["1.1"])
    server, port = await _start_server(app=app, config=config)
    try:
        response = await probe_http11(
            "127.0.0.1",
            port,
            method="POST",
            target="/rpc",
            headers=[("content-type", "application/json")],
            body=b'{"jsonrpc":"2.0","method":"DemoItem.create","params":{"name":"Grace-h11"},"id":101}',
        )
        return _ok("h11-jsonrpc", response.to_jsonable())
    except Exception as exc:
        return _err("h11-jsonrpc", exc)
    finally:
        await _safe_close(server)


async def _h2_rest() -> dict[str, Any]:
    app = build_app()
    config = build_config(host="127.0.0.1", port=0, lifespan="off", http_versions=["2"], enable_h2c=True)
    server, port = await _start_server(app=app, config=config)
    try:
        response = await probe_h2c(
            "127.0.0.1",
            port,
            method="POST",
            path="/items",
            headers=[("content-type", "application/json")],
            body=b'{"name":"Ada-h2"}',
        )
        return _ok("h2-rest", response.to_jsonable())
    except Exception as exc:
        return _err("h2-rest", exc)
    finally:
        await _safe_close(server)


async def _h2_jsonrpc() -> dict[str, Any]:
    app = build_app()
    config = build_config(host="127.0.0.1", port=0, lifespan="off", http_versions=["2"], enable_h2c=True)
    server, port = await _start_server(app=app, config=config)
    try:
        response = await probe_h2c(
            "127.0.0.1",
            port,
            method="POST",
            path="/rpc",
            headers=[("content-type", "application/json")],
            body=b'{"jsonrpc":"2.0","method":"DemoItem.create","params":{"name":"Grace-h2"},"id":201}',
        )
        return _ok("h2-jsonrpc", response.to_jsonable())
    except Exception as exc:
        return _err("h2-jsonrpc", exc)
    finally:
        await _safe_close(server)


async def _h3_rest() -> dict[str, Any]:
    app = build_app()
    config = build_config(
        transport="udp",
        host="127.0.0.1",
        port=0,
        lifespan="off",
        http_versions=["3"],
        protocols=["http3"],
        quic_secret=b"shared",
    )
    server, port = await _start_server(app=app, config=config)
    try:
        response = await probe_h3(
            "127.0.0.1",
            port,
            method="POST",
            path="/items",
            headers=[("content-type", "application/json")],
            body=b'{"name":"Ada-h3"}',
        )
        return _ok("h3-rest", response.to_jsonable())
    except Exception as exc:
        return _err("h3-rest", exc)
    finally:
        await _safe_close(server)


async def _h3_jsonrpc() -> dict[str, Any]:
    app = build_app()
    config = build_config(
        transport="udp",
        host="127.0.0.1",
        port=0,
        lifespan="off",
        http_versions=["3"],
        protocols=["http3"],
        quic_secret=b"shared",
    )
    server, port = await _start_server(app=app, config=config)
    try:
        response = await probe_h3(
            "127.0.0.1",
            port,
            method="POST",
            path="/rpc",
            headers=[("content-type", "application/json")],
            body=b'{"jsonrpc":"2.0","method":"DemoItem.create","params":{"name":"Grace-h3"},"id":301}',
        )
        return _ok("h3-jsonrpc", response.to_jsonable())
    except Exception as exc:
        return _err("h3-jsonrpc", exc)
    finally:
        await _safe_close(server)


async def _h11_streams_and_sse() -> list[dict[str, Any]]:
    app = build_app()
    config = build_config(host="127.0.0.1", port=0, lifespan="off", http_versions=["1.1"])
    server, port = await _start_server(app=app, config=config)
    results: list[dict[str, Any]] = []
    try:
        try:
            raw = await probe_h11_stream("127.0.0.1", port, target="/stream/raw")
            results.append(_ok("stream-raw", raw.to_jsonable()))
        except Exception as exc:
            results.append(_err("stream-raw", exc))
        try:
            ndjson = await probe_h11_stream("127.0.0.1", port, target="/stream/ndjson")
            results.append(_ok("stream-ndjson", ndjson.to_jsonable()))
        except Exception as exc:
            results.append(_err("stream-ndjson", exc))
        try:
            sse = await probe_h11_stream("127.0.0.1", port, target="/sse/events")
            results.append(_ok("sse", sse.to_jsonable()))
        except Exception as exc:
            results.append(_err("sse", exc))
    finally:
        await _safe_close(server)
    return results


async def _websocket_ws() -> dict[str, Any]:
    app = build_app()
    config = build_config(host="127.0.0.1", port=0, lifespan="off", http_versions=["1.1"], websocket=True)
    server, port = await _start_server(app=app, config=config)
    try:
        response = await asyncio.wait_for(
            probe_ws_wss("127.0.0.1", port, path="/ws/echo", text="hello-ws", timeout=3.0),
            timeout=4.0,
        )
        return _ok("ws", response.to_jsonable())
    except Exception as exc:
        return _err("ws", exc)
    finally:
        await _safe_close(server)


async def _websocket_wss() -> dict[str, Any]:
    app = build_app()
    config = build_config(
        host="127.0.0.1",
        port=0,
        lifespan="off",
        http_versions=["1.1"],
        websocket=True,
        ssl_certfile=str(SERVER_CERT),
        ssl_keyfile=str(SERVER_KEY),
    )
    server, port = await _start_server(app=app, config=config)
    try:
        response = await asyncio.wait_for(
            probe_ws_wss(
                "localhost",
                port,
                path="/wss/echo",
                text="hello-wss",
                secure=True,
                cafile=str(SERVER_CERT),
                server_hostname="localhost",
                timeout=3.0,
            ),
            timeout=4.0,
        )
        return _ok("wss", response.to_jsonable())
    except Exception as exc:
        return _err("wss", exc)
    finally:
        await _safe_close(server)


async def _websocket_wss_jsonrpc() -> dict[str, Any]:
    app = build_app()
    config = build_config(
        host="127.0.0.1",
        port=0,
        lifespan="off",
        http_versions=["1.1"],
        websocket=True,
        ssl_certfile=str(SERVER_CERT),
        ssl_keyfile=str(SERVER_KEY),
    )
    server, port = await _start_server(app=app, config=config)
    try:
        payload = json.dumps(
            {"jsonrpc": "2.0", "method": "demo.echo", "params": {"value": 7}, "id": 501},
            separators=(",", ":"),
        )
        response = await asyncio.wait_for(
            probe_ws_wss(
                "localhost",
                port,
                path="/wss/jsonrpc",
                text=payload,
                secure=True,
                cafile=str(SERVER_CERT),
                server_hostname="localhost",
                subprotocols=["jsonrpc"],
                timeout=3.0,
            ),
            timeout=4.0,
        )
        return _ok("wss-jsonrpc", response.to_jsonable())
    except Exception as exc:
        return _err("wss-jsonrpc", exc)
    finally:
        await _safe_close(server)


async def _mtls_http11() -> dict[str, Any]:
    app = build_app()
    with tempfile.TemporaryDirectory() as tmpdir:
        client_cert_pem, client_key_pem = generate_self_signed_certificate("interop-client", purpose="client")
        client_cert = Path(tmpdir) / "client-cert.pem"
        client_key = Path(tmpdir) / "client-key.pem"
        client_cert.write_bytes(client_cert_pem)
        client_key.write_bytes(client_key_pem)
        config = build_config(
            host="127.0.0.1",
            port=0,
            lifespan="off",
            http_versions=["1.1"],
            ssl_certfile=str(SERVER_CERT),
            ssl_keyfile=str(SERVER_KEY),
            ssl_ca_certs=str(client_cert),
            ssl_require_client_cert=True,
        )
        server, port = await _start_server(app=app, config=config)
        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(SERVER_CERT))
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.set_alpn_protocols(["http/1.1"])
            context.load_cert_chain(str(client_cert), str(client_key))
            reader, writer = await asyncio.open_connection(
                "127.0.0.1",
                port,
                ssl=context,
                server_hostname="localhost",
            )
            try:
                writer.write(b"GET /mtls/echo HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                await writer.drain()
                data = await reader.read(65535)
                return _ok("mtls", {"raw_response": data.decode("utf-8", errors="replace")})
            finally:
                writer.close()
                with suppress(Exception):
                    await writer.wait_closed()
        except Exception as exc:
            return _err("mtls", exc)
        finally:
            await _safe_close(server)


async def _webtransport() -> dict[str, Any]:
    app = build_app()
    cert_pem, key_pem = generate_self_signed_certificate("server.example")
    with tempfile.TemporaryDirectory() as tmpdir:
        certfile = Path(tmpdir) / "server-cert.pem"
        keyfile = Path(tmpdir) / "server-key.pem"
        certfile.write_bytes(cert_pem)
        keyfile.write_bytes(key_pem)
        config = build_config(
            transport="udp",
            host="127.0.0.1",
            port=0,
            lifespan="off",
            http_versions=["3"],
            protocols=["webtransport"],
            ssl_certfile=str(certfile),
            ssl_keyfile=str(keyfile),
            webtransport_path="/transport/session",
            webtransport_origins=["https://localhost:8088"],
        )
        server, port = await _start_server(app=app, config=config)
        try:
            response = await probe_wt_stream(
                "127.0.0.1",
                port,
                path=b"/transport/session",
                payload=b"hello-webtransport",
                trusted_certificates=[cert_pem],
            )
            return _ok("webtransport", response.to_jsonable())
        except Exception as exc:
            return _err("webtransport", exc)
        finally:
            await _safe_close(server)


def _unsupported_wss_ndjson() -> dict[str, Any]:
    try:
        _ = build_app()
        return _ok("wss-ndjson", build_fail_closed_examples())
    except Exception as exc:
        return _err("wss-ndjson", exc)


async def main() -> int:
    results: list[dict[str, Any]] = []
    scenarios: list[tuple[str, Any]] = [
        ("h11-rest", _http11_rest),
        ("h11-jsonrpc", _http11_jsonrpc),
        ("h2-rest", _h2_rest),
        ("h2-jsonrpc", _h2_jsonrpc),
        ("h3-rest", _h3_rest),
        ("h3-jsonrpc", _h3_jsonrpc),
        ("h11-streams-and-sse", _h11_streams_and_sse),
        ("ws", _websocket_ws),
        ("wss", _websocket_wss),
        ("wss-jsonrpc", _websocket_wss_jsonrpc),
        ("wss-ndjson", _unsupported_wss_ndjson),
        ("mtls", _mtls_http11),
        ("webtransport", _webtransport),
    ]
    for label, fn in scenarios:
        print(f"RUNNING {label}", file=sys.stderr, flush=True)
        outcome = fn()
        if asyncio.iscoroutine(outcome):
            resolved = await outcome
        else:
            resolved = outcome
        if isinstance(resolved, list):
            results.extend(resolved)
        else:
            results.append(resolved)
    print(json.dumps({"results": results}, indent=2))
    return 0 if all(result.get("ok") for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
