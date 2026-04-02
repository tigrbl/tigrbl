from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CLAIM_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'


GATE_B_PREFIXES = ('OP-', 'CLI-', 'GATE-007', 'GATE-008', 'OAS-006', 'RPC-002', 'RPC-003')
ALLOWED = {'verified in checkpoint', 'implemented', 'de-scoped'}


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


def test_gate_b_surface_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_b_surface_closure.py')
    assert result.returncode == 0, f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'


def test_gate_b_claim_rows_have_closed_or_descoped_status() -> None:
    statuses = _claim_statuses()
    relevant = {
        claim_id: status
        for claim_id, status in statuses.items()
        if claim_id.startswith('OP-') or claim_id.startswith('CLI-') or claim_id in {'GATE-007', 'GATE-008', 'OAS-006', 'RPC-002', 'RPC-003'}
    }
    assert relevant
    bad = {claim_id: status for claim_id, status in relevant.items() if status not in ALLOWED}
    assert not bad, bad


def test_current_target_and_current_state_record_no_open_surface_gaps() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state = CURRENT_STATE.read_text(encoding='utf-8')
    assert '## Current-target surfaces still missing\n\nNone.' in current_target
    assert 'no unresolved current-target surface gaps' in current_state
