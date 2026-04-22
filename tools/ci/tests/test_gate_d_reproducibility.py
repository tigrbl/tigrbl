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
REQUIRED = {'GATE-011', 'GATE-012'}
ALLOWED = {'verified in checkpoint', 'implemented'}


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.run([sys.executable, script], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)


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


def test_gate_d_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_d_reproducibility.py')
    assert result.returncode == 0, f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'


def test_gate_d_claim_rows_have_expected_statuses() -> None:
    statuses = _claim_statuses()
    for claim_id in REQUIRED:
        assert statuses.get(claim_id) in ALLOWED, {claim_id: statuses.get(claim_id)}


def test_current_docs_record_gate_d_pass_and_clean_room_success() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state = CURRENT_STATE.read_text(encoding='utf-8')
    gate_model = GATE_MODEL.read_text(encoding='utf-8')
    assert '- Gate D status: passed in the Gate D reproducibility checkpoint' in current_target
    assert 'clean-room evidence passes on the selected candidate build' in current_state
    assert 'Gate D is passed at checkpoint quality and machine-checked in CI' in gate_model
