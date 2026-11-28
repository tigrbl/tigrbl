import httpx
import pytest
from trace_lab_demo.capture import Capture
from trace_lab_demo.gateway import build_gateway
from trace_lab.http import reply


@pytest.mark.asyncio
async def test_gateway_serves_direct_links_and_runs_only_from_loopback(
    tmp_path, buffer
):
    (tmp_path / "index.html").write_text("<title>Trace Lab</title>")
    capture = Capture(buffer)

    async def app(scope, receive, send):
        await reply(send, 404, {"error": "missing"})

    async def scenario(note_id):
        assert note_id
        capture.add("Invocation", "REST", {"invocation_id": "real-run"})
        return {"rest": "200"}

    gateway = build_gateway(
        app, capture, tmp_path, scenario, reply, lambda: "http://127.0.0.1:8765"
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway), base_url="http://127.0.0.1:8765"
    ) as client:
        assert (await client.get("/distributions")).status_code == 200
        assert (await client.get("/assets/missing.js")).status_code == 404
        assert (
            await client.post("/demo/run", headers={"origin": "https://example.org"})
        ).status_code == 403
        capture.active_run = "busy"
        assert (await client.post("/demo/run")).status_code == 409
        capture.active_run = None
        run = await client.post("/demo/run")
        assert run.status_code == 200
        data = (await client.get("/demo/trace")).json()
        assert data["last_run_summary"] == run.json()
        assert data["events"][0]["scenario_run_id"] == run.json()["run_id"]
