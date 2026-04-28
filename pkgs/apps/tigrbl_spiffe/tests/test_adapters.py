import pytest
import httpx
import ssl

from tigrbl_spiffe.adapters import Endpoint, TigrblClientAdapter, Txn
from tigrbl_spiffe.tls.adapters import httpx_client_with_tls


@pytest.mark.asyncio
async def test_for_endpoint_uds_returns_transaction():
    adapter = TigrblClientAdapter()
    txn = await adapter.for_endpoint(
        Endpoint(scheme="uds", address="unix:///var/run/workload.sock")
    )
    assert isinstance(txn, Txn)
    assert txn.kind == "uds"
    assert txn.uds_path == "/var/run/workload.sock"
    assert txn.http is None


@pytest.mark.asyncio
async def test_for_endpoint_http_creates_async_client():
    adapter = TigrblClientAdapter()
    txn = await adapter.for_endpoint(
        Endpoint(scheme="http", address="http://example.test")
    )
    assert txn.kind == "http"
    assert isinstance(txn.http, httpx.AsyncClient)
    assert str(txn.http.base_url) == "http://example.test"
    await txn.http.aclose()


@pytest.mark.asyncio
async def test_for_endpoint_https_creates_async_client():
    adapter = TigrblClientAdapter()
    txn = await adapter.for_endpoint(
        Endpoint(scheme="https", address="https://secure.test", timeout_s=9.5)
    )
    assert txn.kind == "https"
    assert isinstance(txn.http, httpx.AsyncClient)
    assert txn.http.timeout.read == 9.5
    await txn.http.aclose()


@pytest.mark.asyncio
async def test_for_endpoint_unknown_scheme_raises():
    adapter = TigrblClientAdapter()
    with pytest.raises(ValueError):
        await adapter.for_endpoint(Endpoint(scheme="smtp", address="smtp://example"))


@pytest.mark.asyncio
async def test_httpx_client_with_tls_uses_helper_context(monkeypatch):
    context = ssl.create_default_context()
    captured = {}

    class Helper:
        async def client_context(self):
            return context

    class CapturingAsyncClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", CapturingAsyncClient)

    client = await httpx_client_with_tls("https://secure.test", Helper())

    assert isinstance(client, CapturingAsyncClient)
    assert captured["base_url"] == "https://secure.test"
    assert captured["timeout"] == 10.0
    assert captured["verify"] is context
