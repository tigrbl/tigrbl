from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CLAIM_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
NEXT_TARGETS = REPO_ROOT / 'docs' / 'conformance' / 'NEXT_TARGETS.md'
PACKAGE_PYPROJECT = REPO_ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
REQUIRED = {'HANDOFF-001', 'HANDOFF-002', 'NEXT-001', 'NEXT-002'}


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.run([sys.executable, script], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)


def _claim_rows() -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for line in CLAIM_REGISTRY.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) < 4 or cells[0] in {'Claim ID', '---'}:
            continue
        rows[cells[0]] = (cells[2].lower(), cells[3])
    return rows


def test_phase14_handoff_validator_passes() -> None:
    result = _run('tools/ci/validate_phase14_handoff.py')
    assert result.returncode == 0, f'STDOUT\n{result.stdout}\nSTDERR\n{result.stderr}'


def test_next_line_and_next_target_claim_rows_exist() -> None:
    rows = _claim_rows()
    for claim_id in REQUIRED:
        assert claim_id in rows
    assert rows['HANDOFF-001'][0] == 'verified in checkpoint'
    assert rows['NEXT-001'][0] == 'verified in checkpoint'
    assert rows['NEXT-002'][0] == 'verified in checkpoint'


def test_current_docs_record_active_dev_line_and_frozen_release_history() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state = CURRENT_STATE.read_text(encoding='utf-8')
    next_targets = NEXT_TARGETS.read_text(encoding='utf-8')
    pyproject = PACKAGE_PYPROJECT.read_text(encoding='utf-8')
    assert 'active next-line dev bundle: `docs/conformance/dev/0.3.19.dev1/`' in current_target
    assert 'The active working tree is now `0.3.19.dev1`.' in current_state
    assert 'Stable release `0.3.18` is frozen as current-boundary release history.' in next_targets
    assert 'version = "0.3.19.dev1"' in pyproject
