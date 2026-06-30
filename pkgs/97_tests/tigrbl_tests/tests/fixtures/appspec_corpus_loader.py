from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

CASE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}$")
FIXTURE_DIR = Path(__file__).resolve().parent


def load_corpus(filename: str) -> dict[str, Any]:
    path = FIXTURE_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def validate_corpus(document: dict[str, Any], *, lane: str) -> None:
    if document.get("schema_version") != "1.0.0":
        raise ValueError("schema_version must be 1.0.0")
    if document.get("kind") != "appspec_corpus":
        raise ValueError("kind must be appspec_corpus")
    if document.get("lane") != lane:
        raise ValueError(f"lane must be {lane}")

    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")

    seen_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("every case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not CASE_ID_RE.fullmatch(case_id):
            raise ValueError(f"invalid case id: {case_id!r}")
        if case_id in seen_ids:
            raise ValueError(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)

        if not isinstance(case.get("mode"), str):
            raise ValueError(f"case {case_id} must include mode")
        if not isinstance(case.get("title"), str):
            raise ValueError(f"case {case_id} must include title")
        if not isinstance(case.get("app"), dict):
            raise ValueError(f"case {case_id} must include app object")
        if not isinstance(case.get("table"), dict):
            raise ValueError(f"case {case_id} must include table object")
        if not isinstance(case.get("expect"), dict):
            raise ValueError(f"case {case_id} must include expect object")
