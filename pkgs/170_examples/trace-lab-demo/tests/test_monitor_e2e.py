import os
import socket
import subprocess
import sys
import time
from contextlib import ExitStack
from pathlib import Path
from uuid import uuid4

import httpx
import pytest


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def start(stack, port, env, log_path, module):
    frontend = (
        Path(__file__).resolve().parents[4] / "pkgs/130_frontend/trace-lab-ui/dist"
    )
    with log_path.open("wb") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                module,
                "--port",
                str(port),
                "--frontend",
                str(frontend),
            ],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    stack.callback(stop, process)
    return process


def stop(process):
    if process.poll() is None:
        process.terminate()
        process.wait(timeout=10)


def eventually(check, process, log):
    deadline = time.monotonic() + 15
    while process.poll() is None and time.monotonic() < deadline:
        try:
            if result := check():
                return result
        except httpx.TransportError:
            pass
        time.sleep(0.1)
    pytest.fail(
        f"Service or expected trace did not become available:\n{log.read_text()}"
    )


@pytest.mark.skipif(
    not os.environ.get("TRACE_TEST_POSTGRES_URL"),
    reason="requires a disposable Postgres database",
)
def test_primary_exports_to_independent_collector(tmp_path):
    collector_port = free_port()
    collector_url = f"http://127.0.0.1:{collector_port}"
    collector_log = tmp_path / "collector.log"
    primary_port = free_port()
    primary_url = f"http://127.0.0.1:{primary_port}"
    primary_log = tmp_path / "primary.log"
    auth = ("operator", uuid4().hex)
    token = uuid4().hex
    env = {
        **os.environ,
        "TRACE_DATABASE_URL": os.environ["TRACE_TEST_POSTGRES_URL"],
        "TRACE_OPERATOR_USER": auth[0],
        "TRACE_OPERATOR_PASSWORD": auth[1],
        "TRACE_INGEST_TOKEN": token,
    }
    with ExitStack() as stack, httpx.Client(timeout=2, trust_env=False) as client:
        collector = start(stack, collector_port, env, collector_log, "trace_lab.run")
        html = eventually(
            lambda: client.get(collector_url, auth=auth), collector, collector_log
        )
        assert "data-trace-monitor" in html.text
        assert 'rel="icon" type="image/svg+xml" href="/favicon.svg"' in html.text
        favicon = client.get(collector_url + "/favicon.svg")
        assert favicon.is_success and favicon.headers["content-type"].startswith(
            "image/svg+xml"
        )
        primary = start(
            stack,
            primary_port,
            {**env, "TRACE_COLLECTOR_URL": collector_url},
            primary_log,
            "trace_lab_demo.run",
        )
        eventually(lambda: client.get(primary_url), primary, primary_log)

        def write_note():
            result = client.post(
                primary_url + "/notes", json={"id": uuid4().hex, "name": "Trace proof"}
            )
            assert result.is_success, result.text
            return result.headers["x-correlation-id"]

        def read_trace(correlation):
            result = client.get(
                collector_url + "/api/timeline",
                params={"correlation_id": correlation},
                auth=auth,
            )
            assert result.is_success, result.text
            events = result.json()["events"]
            expected = {"http.response.sent", "invocation.completed", "db.tx.commit"}
            return expected <= {event["kind"] for event in events}

        correlation = write_note()
        eventually(lambda: read_trace(correlation), collector, collector_log)
        for query in (
            {},
            {"id": correlation},
        ):
            evidence = client.get(
                collector_url + "/api/correlations", params=query, auth=auth
            )
            assert evidence.is_success, evidence.text
            rows = [
                event
                for event in evidence.json()["events"]
                if event.get("correlation_id") == correlation
            ]
            response = next(
                event for event in rows if event["kind"] == "http.response.sent"
            )
            assert response["http_status"] == 201
            assert any(event["kind"] == "db.tx.participant" for event in rows)
        invocation = next(
            event["invocation_id"]
            for event in rows
            if event["kind"] == "invocation.completed"
        )
        typed = client.get(
            collector_url + "/api/correlations",
            params={"id_type": "invocation_id", "id": invocation},
            auth=auth,
        )
        assert typed.is_success, typed.text
        assert {event["correlation_id"] for event in typed.json()["events"]} == {
            correlation
        }
        batch = {
            "version": 1,
            "service": "replay-test",
            "environment": "test",
            "worker_boot_id": uuid4().hex,
            "events": [
                {
                    "sequence": 1,
                    "kind": "Invocation",
                    "transport": "REST",
                    "captured_at": "2026-11-25T12:00:00Z",
                    "fields": {"invocation_id": "replay-test"},
                }
            ],
        }
        for expected in (1, 0):
            result = client.post(
                collector_url + "/internal/trace/batches",
                headers={"Authorization": f"Bearer {token}"},
                json=batch,
            )
            assert result.is_success, result.text
            assert result.json()["inserted"] == expected

        stop(collector)
        during_outage = write_note()
        collector = start(stack, collector_port, env, collector_log, "trace_lab.run")
        eventually(lambda: read_trace(correlation), collector, collector_log)
        eventually(lambda: read_trace(during_outage), collector, collector_log)
