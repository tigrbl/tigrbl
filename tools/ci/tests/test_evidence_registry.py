from __future__ import annotations

import os
import subprocess
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import re

REPO_ROOT = Path(__file__).resolve().parents[3]
CLAIM_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
EVIDENCE_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'EVIDENCE_REGISTRY.json'
CLAIM_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|')


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.run(
        [sys.executable, script],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def _claim_ids() -> set[str]:
    ids: set[str] = set()
    for line in CLAIM_REGISTRY.read_text(encoding='utf-8').splitlines():
        match = CLAIM_RE.match(line)
        if not match:
            continue
        claim_id = match.group(1).strip()
        if claim_id in {'Claim ID', '---'}:
            continue
        if re.match(r'^(?:[A-Z]+-\d+|RFC-\d+|OIDC-\d+)$', claim_id):
            ids.add(claim_id)
    return ids


def test_claim_registry_rows_are_covered_by_evidence_registry() -> None:
    data = json.loads(EVIDENCE_REGISTRY.read_text(encoding='utf-8'))
    claims = set(data['claims'])
    assert _claim_ids() <= claims


def test_evidence_registry_and_bundle_validators_pass() -> None:
    failures: list[str] = []
    for script in (
        'tools/ci/validate_evidence_registry.py',
        'tools/ci/validate_evidence_bundles.py',
    ):
        result = _run(script)
        if result.returncode != 0:
            failures.append(f"{script}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    assert not failures, '\n\n'.join(failures)
