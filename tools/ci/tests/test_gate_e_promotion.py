from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CLAIM_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
GATE_MODEL = REPO_ROOT / 'docs' / 'conformance' / 'GATE_MODEL.md'
README = REPO_ROOT / 'README.md'
REQUIRED = {'GATE-013', 'GATE-014', 'CERT-001', 'CERT-002'}
STABLE_RELEASE_RE = re.compile(r'promoted stable release:\s*`docs/conformance/releases/([^`/]+)/`')


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


def test_gate_e_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_e_promotion.py')
    assert result.returncode == 0, f'STDOUT\n{result.stdout}\nSTDERR\n{result.stderr}'


def test_gate_e_claim_rows_have_expected_statuses() -> None:
    rows = _claim_rows()
    for claim_id in REQUIRED:
        assert claim_id in rows
    assert rows['CERT-001'][0] == 'achieved'
    assert rows['CERT-001'][1].lower().startswith('tier 3')
    assert rows['CERT-002'][0] == 'achieved'
    assert rows['CERT-002'][1].lower().startswith('tier 3')
    assert rows['GATE-013'][0] in {'verified in checkpoint', 'achieved'}
    assert rows['GATE-014'][0] in {'implemented', 'verified in checkpoint'}


def test_current_docs_record_gate_e_pass_and_frozen_release_history() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state = CURRENT_STATE.read_text(encoding='utf-8')
    gate_model = GATE_MODEL.read_text(encoding='utf-8')
    readme = README.read_text(encoding='utf-8')
    match = STABLE_RELEASE_RE.search(current_target)
    assert match is not None
    stable_release_version = match.group(1)
    assert '- Gate E status: passed in the Gate E promotion checkpoint' in current_target
    assert 'Gate E: passed in the Gate E promotion checkpoint' in current_state
    assert 'Gate E is passed in the Gate E promotion checkpoint' in gate_model
    assert f'promoted stable release: `docs/conformance/releases/{stable_release_version}/`' in current_target
    assert 'docs/conformance/releases/' in readme
    assert 'docs/conformance/dev/' in readme
