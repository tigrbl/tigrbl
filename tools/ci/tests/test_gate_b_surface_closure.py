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


GATE_B_PREFIXES = ('OP-', 'CLI-', 'GATE-007', 'GATE-008', 'OAS-006', 'RPC-002', 'RPC-003')


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


def test_gate_b_surface_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_b_surface_closure.py')
    assert result.returncode == 0, f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'


def test_gate_b_claim_rows_have_closed_or_descoped_status() -> None:
    rows = legacy_claim_rows()
    relevant = {
        claim_id: row
        for claim_id, row in rows.items()
        if claim_id.startswith('OP-') or claim_id.startswith('CLI-') or claim_id in {'GATE-007', 'GATE-008', 'OAS-006', 'RPC-002', 'RPC-003'}
    }
    assert relevant
    bad = {claim_id: row.status for claim_id, row in relevant.items() if not is_claim_passing(row)}
    assert not bad, bad


def test_conformance_docs_declare_ssot_as_authority() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    conformance_readme = CONFORMANCE_README.read_text(encoding='utf-8')
    assert '## Current-target surfaces still missing\n\nNone.' in current_target
    assert '.ssot/registry.json' in conformance_readme
    assert 'non-authoritative projection' in conformance_readme
