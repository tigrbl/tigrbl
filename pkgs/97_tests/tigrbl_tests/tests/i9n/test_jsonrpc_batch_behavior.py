import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_jsonrpc_batch_executes_in_order(app_client):
    client, _, _ = app_client

    batch_resp = await client.post(
        "/rpc/",
        json=[
            {
                "jsonrpc": "2.0",
                "method": "Tenant.create",
                "params": {"name": "batch-tenant"},
                "id": 1,
            },
            {
                "jsonrpc": "2.0",
                "method": "Tenant.list",
                "params": {},
                "id": 2,
            },
        ],
    )

    assert batch_resp.status_code == 200
    responses = batch_resp.json()
    assert [response["id"] for response in responses] == [1, 2]
    assert responses[0]["result"]["name"] == "batch-tenant"
    assert {tenant["name"] for tenant in responses[1]["result"]} >= {"batch-tenant"}


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_jsonrpc_batch_reports_errors_per_item(app_client):
    client, _, _ = app_client

    batch_resp = await client.post(
        "/rpc/",
        json=[
            {
                "jsonrpc": "2.0",
                "method": "Tenant.list",
                "params": {},
                "id": 10,
            },
            {
                "jsonrpc": "2.0",
                "method": "Tenant",
                "params": {},
                "id": 11,
            },
        ],
    )

    assert batch_resp.status_code == 200
    responses = batch_resp.json()
    assert [response["id"] for response in responses] == [10, 11]
    assert "result" in responses[0]
    assert responses[1]["error"]["code"] == -32601
    assert responses[1]["error"]["message"] == "Method not found"


@pytest.mark.asyncio
async def test_rest_and_jsonrpc_response_correlation_is_request_scoped(app_client):
    client, _, _ = app_client
    headers = {"X-Correlation-ID": "untrusted-client-value"}
    rest = await client.get("/tenant", headers=headers)
    rpc = await client.post("/rpc/", headers=headers, json={
        "jsonrpc": "2.0", "method": "Tenant.list", "params": {}, "id": "client-id",
    })
    missing = await client.get("/correlation-probe-missing", headers=headers)

    assert (rest.status_code, rpc.status_code, missing.status_code) == (200, 200, 404)
    assert rpc.json()["id"] == "client-id"
    correlations = {response.headers["x-correlation-id"] for response in (rest, rpc, missing)}
    assert len(correlations) == 3
    assert "untrusted-client-value" not in correlations
    assert "client-id" not in correlations
