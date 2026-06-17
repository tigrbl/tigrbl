from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / 'tools' / 'ci'))

CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CONFORMANCE_README = REPO_ROOT / 'docs' / 'conformance' / 'README.md'
README = REPO_ROOT / 'README.md'
REQUIRED = {'GATE-013', 'GATE-014', 'CERT-001', 'CERT-002'}
STABLE_RELEASE_RE = re.compile(r'promoted stable release:\s*`docs/conformance/releases/([^`/]+)/`')

from ssot_legacy_authority import is_claim_passing, legacy_claim_rows  # noqa: E402


def _is_t3(tier: str) -> bool:
    normalized = tier.lower().replace(' ', '')
    return normalized.startswith('t3') or normalized.startswith('tier3')


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.run([sys.executable, script], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)


def _claim_rows() -> dict[str, tuple[str, str]]:
    return {display_id: (row.status, row.tier) for display_id, row in legacy_claim_rows().items()}


def test_gate_e_validator_passes() -> None:
    result = _run('tools/ci/validate_gate_e_promotion.py')
    assert result.returncode == 0, f'STDOUT\n{result.stdout}\nSTDERR\n{result.stderr}'


def test_gate_e_claim_rows_have_expected_statuses() -> None:
    rows = legacy_claim_rows()
    for claim_id in REQUIRED:
        assert claim_id in rows
        assert is_claim_passing(rows[claim_id]), {claim_id: rows[claim_id].status}
    assert _is_t3(rows['CERT-001'].tier)
    assert _is_t3(rows['CERT-002'].tier)


def test_current_docs_record_gate_e_history_and_ssot_authority() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    conformance_readme = CONFORMANCE_README.read_text(encoding='utf-8')
    readme = README.read_text(encoding='utf-8')
    match = STABLE_RELEASE_RE.search(current_target)
    assert match is not None
    stable_release_version = match.group(1)
    assert '- Gate E status: passed in the Gate E promotion checkpoint' in current_target
    assert f'promoted stable release: `docs/conformance/releases/{stable_release_version}/`' in current_target
    assert '.ssot/registry.json' in conformance_readme
    assert 'non-authoritative projection' in conformance_readme
    assert 'docs/conformance/releases/' in readme
    assert 'docs/conformance/dev/' in readme
