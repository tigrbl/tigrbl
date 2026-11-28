"""Verify Notes Pilot export through a running Trace Lab collector."""

import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
from uuid import uuid4

import httpx


def eventually(fetch, process=None):
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise RuntimeError(f"Service exited with status {process.returncode}")
        try:
            if result := fetch():
                return result
        except httpx.TransportError:
            pass
        time.sleep(0.2)
    raise RuntimeError("Timed out waiting for the trace service")


def verify_browser(url, credentials, correlation, expected_image_version=None):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get("TRACE_VERIFY_CHROME")
        )
        page = browser.new_page(
            http_credentials={
                "username": credentials[0],
                "password": credentials[1],
                "origin": url,
                "send": "always",
            }
        )
        page.goto(f"{url}/correlations?" + urlencode({"q": f"corr:{correlation}"}))
        waterfall = page.get_by_test_id("waterfall-svg")
        if not waterfall.is_visible():
            page.locator("td button.text-left").first.click()
        waterfall.wait_for()
        direct = page.url
        page.goto(direct)
        waterfall.wait_for()
        labels = page.locator(
            '[data-testid="waterfall-scroll-container"] span[title].truncate'
        ).evaluate_all(
            """labels => labels.map(label => [
                label.title,
                parseFloat(label.parentElement.parentElement.parentElement.parentElement.style.paddingLeft)
            ])"""
        )
        phase = next(i for i, (label, _) in enumerate(labels) if label == "START_TX")
        tx = next(
            i
            for i in range(phase + 1, len(labels))
            if labels[i][0].startswith("Transaction ")
        )
        begin = next(
            i for i in range(tx + 1, len(labels)) if labels[i][0] == "db.tx.begin"
        )
        assert labels[phase][1] < labels[tx][1] < labels[begin][1], labels
        if expected_image_version is not None:
            workspace = Path(__file__).resolve().parents[4]
            manifest = workspace / "pkgs/130_frontend/trace-lab-ui/package.json"
            frontend_version = json.loads(manifest.read_text(encoding="utf-8"))[
                "version"
            ]
            expected = {
                "backend": version("tigrbl-transport-trace-lab"),
                "frontend": frontend_version,
                "image": expected_image_version,
            }
            for component, expected_version in expected.items():
                displayed = page.get_by_test_id(f"{component}-version").inner_text()
                assert displayed == f"v{expected_version}", (
                    component,
                    displayed,
                    expected_version,
                )
            print(
                "Footer versions verified:",
                ", ".join(f"{k} v{v}" for k, v in expected.items()),
            )
        return direct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", default="http://127.0.0.1:8766")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--expect-image-version")
    args = parser.parse_args()
    if args.expect_image_version is not None and not args.browser:
        parser.error("--expect-image-version requires --browser")
    collector = args.collector.rstrip("/")
    credentials = (
        os.environ["TRACE_OPERATOR_USER"],
        os.environ["TRACE_OPERATOR_PASSWORD"],
    )
    with (
        tempfile.TemporaryDirectory() as scratch,
        httpx.Client(timeout=5, trust_env=False) as client,
    ):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        pilot = f"http://127.0.0.1:{port}"
        environment = {
            **os.environ,
            "TRACE_COLLECTOR_URL": collector,
            "TRACE_NOTES_DATABASE": str(Path(scratch) / "notes.sqlite3"),
            "TRACE_NOTES_PORT": str(port),
        }
        with subprocess.Popen(
            [sys.executable, "-m", "trace_lab_demo.notes_pilot"], env=environment
        ) as process:
            try:
                eventually(lambda: client.get(collector, auth=credentials).is_success)
                eventually(lambda: client.get(pilot).is_success, process)
                note = client.post(
                    f"{pilot}/notes",
                    json={"id": str(uuid4()), "text": "Trace Lab verification"},
                )
                assert note.status_code == 201, note.text
                correlation = note.headers["x-correlation-id"]

                def read_events():
                    response = client.get(
                        f"{collector}/api/correlations",
                        params={"id": correlation, "id_type": "correlation_id"},
                        auth=credentials,
                    )
                    response.raise_for_status()
                    events = response.json()["events"]
                    expected = {
                        "db.tx.begin",
                        "db.tx.commit",
                        "invocation.completed",
                        "http.response.sent",
                    }
                    return (
                        events
                        if expected <= {event["kind"] for event in events}
                        else None
                    )

                events = eventually(read_events, process)
                assert all(event["correlation_id"] == correlation for event in events)
                assert all(
                    event["metadata"]["service"] == "notes-pilot" for event in events
                )
                assert any(
                    e["kind"] == "http.response.sent" and e["http_status"] == 201
                    for e in events
                )
                phases = {e.get("atom_label"): e.get("atom_phase") for e in events}
                assert phases["fused:compiled_context_setup"] == "INGRESS_BEGIN"
                assert phases["fused:compiled_input_prepare"] == "INGRESS_PARSE"
                assert phases["fused:compiled_validate_and_assemble"] == "PRE_HANDLER"
                print(
                    f"Notes Pilot correlation {correlation} returned {len(events)} projected events"
                )
                if args.browser:
                    print(
                        verify_browser(
                            collector,
                            credentials,
                            correlation,
                            args.expect_image_version,
                        )
                    )
            finally:
                if process.poll() is None:
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                            capture_output=True,
                            check=False,
                        )
                    else:
                        process.terminate()
                    process.wait(timeout=5)


if __name__ == "__main__":
    main()
