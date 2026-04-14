from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:8765"


def curl(*args: str) -> str:
    completed = subprocess.run(
        ["curl.exe", "--silent", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def main() -> int:
    healthz = curl(f"{BASE_URL}/healthz")
    rest_create = curl(
        "--request",
        "POST",
        "--header",
        "Content-Type: application/json",
        "--data-binary",
        f"@{ROOT / 'rest-create.json'}",
        f"{BASE_URL}/users",
    )
    rest_read = curl(f"{BASE_URL}/users/u1")
    rpc_create = curl(
        "--request",
        "POST",
        "--header",
        "Content-Type: application/json",
        "--data-binary",
        f"@{ROOT / 'rpc-create.json'}",
        f"{BASE_URL}/rpc",
    )
    rpc_read = curl(
        "--request",
        "POST",
        "--header",
        "Content-Type: application/json",
        "--data-binary",
        f"@{ROOT / 'rpc-read.json'}",
        f"{BASE_URL}/rpc",
    )
    payload = {
        "healthz": json.loads(healthz),
        "rest_create": json.loads(rest_create),
        "rest_read": json.loads(rest_read),
        "rpc_create": json.loads(rpc_create),
        "rpc_read": json.loads(rpc_read),
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
