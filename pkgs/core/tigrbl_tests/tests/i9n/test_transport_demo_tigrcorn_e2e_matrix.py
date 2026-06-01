from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import ssl
import sys
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any

import pytest
import websockets

ROOT = Path(__file__).resolve().parents[5]
TIGRCORN_ROOT = ROOT.parent / "tigrcorn"
for src_dir in sorted((TIGRCORN_ROOT / "pkgs").glob("*/src")):
    sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(TIGRCORN_ROOT / "src"))
sys.path.insert(0, str(TIGRCORN_ROOT))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_h11_http1_client = _load_module(
    "tigrcorn_h11_http1_client",
    TIGRCORN_ROOT / "tests" / "fixtures_third_party" / "h11_http1_client.py",
)
_h11_stream_client = _load_module(
    "tigrcorn_h11_stream_client",
    TIGRCORN_ROOT / "tests" / "fixtures_third_party" / "h11_stream_client.py",
)
_h2_http2_client = _load_module(
    "tigrcorn_h2_http2_client",
    TIGRCORN_ROOT / "tests" / "fixtures_third_party" / "h2_http2_client.py",
)
_h3_http3_client = _load_module(
    "tigrcorn_h3_http3_client",
    TIGRCORN_ROOT / "tests" / "fixtures_third_party" / "h3_http3_client.py",
)
_ws_wss_client = _load_module(
    "tigrcorn_ws_wss_client",
    TIGRCORN_ROOT / "tests" / "fixtures_third_party" / "ws_wss_client.py",
)
_wt_stream_client = _load_module(
    "tigrcorn_wt_stream_client",
    TIGRCORN_ROOT / "tests" / "fixtures_third_party" / "wt_stream_client.py",
)

probe_http11 = _h11_http1_client.probe_http11
probe_h11_stream = _h11_stream_client.probe_h11_stream
probe_h2c = _h2_http2_client.probe_h2c
probe_h3 = _h3_http3_client.probe_h3
probe_ws_wss = _ws_wss_client.probe_ws_wss
probe_wt_stream = _wt_stream_client.probe_wt_stream

from tigrcorn.config.load import build_config  # noqa: E402
from tigrcorn.server.runner import TigrCornServer  # noqa: E402
from tigrcorn.transports.quic.handshake import generate_self_signed_certificate  # noqa: E402


CERTS = TIGRCORN_ROOT / "tests" / "fixtures_certs"
SERVER_CERT = CERTS / "interop-localhost-cert.pem"
SERVER_KEY = CERTS / "interop-localhost-key.pem"
APP_PATH = ROOT / "examples" / "transport_demo" / "app.py"
_TEMP_DEMO_DBS: list[tempfile.TemporaryDirectory[str]] = []


def _load_transport_demo_app_module(tempdir: tempfile.TemporaryDirectory[str]) -> Any:
    spec = importlib.util.spec_from_file_location("transport_demo_app", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load transport demo app from {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    default_db = Path(tempdir.name) / "transport_demo_default.sqlite3"
    old_db = os.environ.get("TIGRBL_TRANSPORT_DEMO_DB")
    os.environ["TIGRBL_TRANSPORT_DEMO_DB"] = str(default_db)
    try:
        spec.loader.exec_module(module)
    finally:
        if old_db is None:
            os.environ.pop("TIGRBL_TRANSPORT_DEMO_DB", None)
        else:
            os.environ["TIGRBL_TRANSPORT_DEMO_DB"] = old_db
    return module


def build_app() -> Any:
    tempdir = tempfile.TemporaryDirectory(prefix="tigrbl-transport-demo-")
    _TEMP_DEMO_DBS.append(tempdir)
    module = _load_transport_demo_app_module(tempdir)
    return module.build_app(db_path=Path(tempdir.name) / "transport_demo.sqlite3")


def build_fail_closed_examples() -> dict[str, str]:
    tempdir = tempfile.TemporaryDirectory(prefix="tigrbl-transport-demo-")
    _TEMP_DEMO_DBS.append(tempdir)
    module = _load_transport_demo_app_module(tempdir)
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


def _assert_ok(result: dict[str, Any]) -> None:
    assert result.get("ok") is True, result


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


async def _websocket_wss_jsonrpc_invalid_json() -> dict[str, Any]:
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
        context = _ws_wss_client.build_client_ssl_context(str(SERVER_CERT))
        async with websockets.connect(
            f"wss://localhost:{port}/wss/jsonrpc",
            ssl=context,
            server_hostname="localhost",
            subprotocols=["jsonrpc"],
        ) as websocket:
            await websocket.send("not-json")
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.5)
            except websockets.exceptions.ConnectionClosed as exc:
                close_code = getattr(getattr(exc, "rcvd", None), "code", None)
                if close_code is None:
                    close_code = getattr(websocket, "close_code", None)
                return _ok(
                    "wss-jsonrpc-invalid-json",
                    {"close_code": close_code, "subprotocol": websocket.subprotocol},
                )
            return _err(
                "wss-jsonrpc-invalid-json",
                AssertionError("invalid JSON should close the websocket"),
            )
    except Exception as exc:
        return _err("wss-jsonrpc-invalid-json", exc)
    finally:
        await _safe_close(server)


async def _websocket_wss_jsonrpc_wrong_subprotocol() -> dict[str, Any]:
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
        context = _ws_wss_client.build_client_ssl_context(str(SERVER_CERT))
        try:
            async with websockets.connect(
                f"wss://localhost:{port}/wss/jsonrpc",
                ssl=context,
                server_hostname="localhost",
                subprotocols=["not-jsonrpc"],
            ) as websocket:
                await websocket.send('{"jsonrpc":"2.0","method":"demo.echo","params":{"value":7},"id":1}')
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=1.5)
                except websockets.exceptions.ConnectionClosed as exc:
                    close_code = getattr(getattr(exc, "rcvd", None), "code", None)
                    if close_code is None:
                        close_code = getattr(websocket, "close_code", None)
                    return _ok(
                        "wss-jsonrpc-wrong-subprotocol",
                        {"mode": "closed", "close_code": close_code, "subprotocol": websocket.subprotocol},
                    )
                return _err(
                    "wss-jsonrpc-wrong-subprotocol",
                    AssertionError("wrong subprotocol must not receive a JSON-RPC reply"),
                )
        except websockets.exceptions.InvalidStatus as exc:
            return _ok("wss-jsonrpc-wrong-subprotocol", {"mode": "handshake-refused", "status": exc.response.status_code})
    except Exception as exc:
        return _err("wss-jsonrpc-wrong-subprotocol", exc)
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
                with suppress(Exception):
                    writer.close()
        except Exception as exc:
            return _err("mtls", exc)
        finally:
            await _safe_close(server)


async def _mtls_http11_missing_client_cert() -> dict[str, Any]:
    app = build_app()
    with tempfile.TemporaryDirectory() as tmpdir:
        client_cert_pem, _client_key_pem = generate_self_signed_certificate("interop-client", purpose="client")
        client_cert = Path(tmpdir) / "client-cert.pem"
        client_cert.write_bytes(client_cert_pem)
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
            try:
                reader, writer = await asyncio.open_connection(
                    "127.0.0.1",
                    port,
                    ssl=context,
                    server_hostname="localhost",
                )
            except Exception as exc:
                return _ok("mtls-missing-client-cert", {"error": type(exc).__name__, "message": str(exc)})
            try:
                writer.write(b"GET /mtls/echo HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                await writer.drain()
                try:
                    data = await reader.read(65535)
                except Exception as exc:
                    return _ok("mtls-missing-client-cert", {"error": type(exc).__name__, "message": str(exc)})
                if not data:
                    return _ok("mtls-missing-client-cert", {"error": "connection-closed"})
                return _err(
                    "mtls-missing-client-cert",
                    AssertionError(f"unexpected response without client cert: {data!r}"),
                )
            finally:
                with suppress(Exception):
                    writer.close()
        finally:
            await _safe_close(server)


async def _http11_jsonrpc_invalid_method() -> dict[str, Any]:
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
            body=b'{"jsonrpc":"2.0","method":"DemoItem.unknown","params":{},"id":401}',
        )
        return _ok("h11-jsonrpc-invalid-method", response.to_jsonable())
    except Exception as exc:
        return _err("h11-jsonrpc-invalid-method", exc)
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


async def _run_matrix_scenarios() -> list[dict[str, Any]]:
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
    for _label, fn in scenarios:
        outcome = fn()
        resolved = await outcome if asyncio.iscoroutine(outcome) else outcome
        if isinstance(resolved, list):
            results.extend(resolved)
        else:
            results.append(resolved)
    return results


@pytest.mark.asyncio
async def test_transport_demo_tigrcorn_e2e_matrix() -> None:
    results = await _run_matrix_scenarios()
    failures = [result for result in results if not result.get("ok")]
    assert not failures, failures


@pytest.mark.asyncio
async def test_tigrcorn_websocket_handshake_e2e() -> None:
    ws_result = await _websocket_ws()
    wss_result = await _websocket_wss()

    _assert_ok(ws_result)
    _assert_ok(wss_result)

    assert ws_result["payload"]["received_text"] == "ws:hello-ws"
    assert wss_result["payload"]["received_text"] == "wss:hello-wss"
    assert wss_result["payload"]["tls"]["selected_alpn_protocol"] == "http/1.1"


@pytest.mark.asyncio
async def test_tigrcorn_wss_jsonrpc_e2e() -> None:
    result = await _websocket_wss_jsonrpc()

    _assert_ok(result)

    payload = result["payload"]
    assert payload["subprotocol"] == "jsonrpc"
    body = json.loads(payload["received_text"])
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == 501
    assert body["result"]["transport"] == "wss-jsonrpc"
    assert body["result"]["method"] == "demo.echo"
    assert body["result"]["params"] == {"value": 7}


@pytest.mark.asyncio
async def test_tigrcorn_wss_jsonrpc_t2_negative_behaviors() -> None:
    invalid_json = await _websocket_wss_jsonrpc_invalid_json()
    wrong_subprotocol = await _websocket_wss_jsonrpc_wrong_subprotocol()

    _assert_ok(invalid_json)
    _assert_ok(wrong_subprotocol)

    assert invalid_json["payload"]["subprotocol"] == "jsonrpc"
    assert invalid_json["payload"]["close_code"] == 1002
    assert wrong_subprotocol["payload"]["mode"] in {"closed", "handshake-refused"}
    if wrong_subprotocol["payload"]["mode"] == "closed":
        assert wrong_subprotocol["payload"]["close_code"] == 1002


@pytest.mark.asyncio
async def test_transport_demo_t2_negative_http_and_mtls_cases() -> None:
    bad_rpc = await _http11_jsonrpc_invalid_method()
    no_cert = await _mtls_http11_missing_client_cert()

    _assert_ok(bad_rpc)
    _assert_ok(no_cert)

    rpc_payload = bad_rpc["payload"]
    assert rpc_payload["status"] == 200
    rpc_body = json.loads(rpc_payload["body"])
    assert rpc_body["jsonrpc"] == "2.0"
    assert "error" in rpc_body
    assert no_cert["payload"]


@pytest.mark.asyncio
async def test_tigrcorn_webtransport_single_session_demo() -> None:
    result = await _webtransport()

    _assert_ok(result)

    payload = result["payload"]
    assert payload["status"] == 200
    assert payload["body"] == "hello-webtransport"
    assert payload["received_initial_headers"] is True
    assert payload["ended"] is True
    assert payload["remote_settings"]
    assert payload["datagrams_received"] >= 1


async def main() -> int:
    results = await _run_matrix_scenarios()
    print(json.dumps({"results": results}, indent=2))
    return 0 if all(result.get("ok") for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
