from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / 'tools' / 'ci'))

CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CONFORMANCE_README = REPO_ROOT / 'docs' / 'conformance' / 'README.md'

from ssot_legacy_authority import is_claim_passing, legacy_claim_rows  # noqa: E402

RETAINED = {
    'OAS-001', 'OAS-002', 'OAS-003', 'OAS-004', 'OAS-005', 'OAS-006',
    'SEC-001', 'SEC-002', 'SEC-003', 'SEC-004', 'SEC-005', 'SEC-006',
    'RPC-001', 'RPC-002', 'RPC-003', 'RFC-7235', 'RFC-7617', 'RFC-6750',
}
DESCOPED = {
    'OIDC-001', 'RFC-6749', 'RFC-7519', 'RFC-7636',
    'RFC-8414', 'RFC-8705', 'RFC-9110', 'RFC-9449',
}

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
    return {display_id: row.status for display_id, row in legacy_claim_rows().items()}


def test_gate_c_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_c_conformance_security.py')
    assert result.returncode == 0, f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'


def test_retained_and_descoped_claim_rows_have_expected_statuses() -> None:
    rows = legacy_claim_rows()
    for claim_id in RETAINED:
        assert claim_id in rows
        assert is_claim_passing(rows[claim_id]), {claim_id: rows[claim_id].status}
    for claim_id in DESCOPED:
        assert claim_id in rows
        assert is_claim_passing(rows[claim_id]), {claim_id: rows[claim_id].status}


def test_current_docs_record_gate_c_history_and_ssot_authority() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    conformance_readme = CONFORMANCE_README.read_text(encoding='utf-8')
    assert '- Gate C status: passed in the Gate C conformance/security checkpoint' in current_target
    assert '.ssot/registry.json' in conformance_readme
    assert 'non-authoritative projection' in conformance_readme
