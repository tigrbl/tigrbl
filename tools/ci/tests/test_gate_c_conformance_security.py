from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CLAIM_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
GATE_MODEL = REPO_ROOT / 'docs' / 'conformance' / 'GATE_MODEL.md'

RETAINED = {
    'OAS-001', 'OAS-002', 'OAS-003', 'OAS-004', 'OAS-005', 'OAS-006',
    'SEC-001', 'SEC-002', 'SEC-003', 'SEC-004', 'SEC-005', 'SEC-006',
    'RPC-001', 'RPC-002', 'RPC-003', 'RFC-7235', 'RFC-7617', 'RFC-6750',
}
DESCOPED = {
    'OIDC-001', 'RFC-6749', 'RFC-7519', 'RFC-7636',
    'RFC-8414', 'RFC-8705', 'RFC-9110', 'RFC-9449',
}
ALLOWED = {'verified in checkpoint', 'implemented'}


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


def _claim_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in CLAIM_REGISTRY.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) < 3 or cells[0] in {'Claim ID', '---'}:
            continue
        statuses[cells[0]] = cells[2].lower()
    return statuses


def test_gate_c_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_c_conformance_security.py')
    assert result.returncode == 0, f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'


def test_retained_and_descoped_claim_rows_have_expected_statuses() -> None:
    statuses = _claim_statuses()
    for claim_id in RETAINED:
        assert statuses.get(claim_id) in ALLOWED, {claim_id: statuses.get(claim_id)}
    for claim_id in DESCOPED:
        status = statuses.get(claim_id)
        assert status is not None and status.startswith('de-scoped'), {claim_id: status}


def test_current_docs_record_gate_c_pass_and_no_open_spec_security_gaps() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state = CURRENT_STATE.read_text(encoding='utf-8')
    gate_model = GATE_MODEL.read_text(encoding='utf-8')
    assert '- Gate C status: passed in the Phase 11 checkpoint' in current_target
    assert 'no unresolved retained spec/security gaps remain' in current_state
    assert 'Gate C is passed at checkpoint quality and machine-checked in CI' in gate_model
