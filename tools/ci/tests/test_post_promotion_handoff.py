from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / 'tools' / 'ci'))

CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
PACKAGE_PYPROJECT = REPO_ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
REGISTRY = REPO_ROOT / '.ssot' / 'registry.json'
REQUIRED = {'HANDOFF-001', 'HANDOFF-002', 'NEXT-001', 'NEXT-002'}
VERSION_RE = re.compile(r'^([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.dev([0-9]+))?$')

from ssot_legacy_authority import is_claim_passing, legacy_claim_rows  # noqa: E402


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.run([sys.executable, script], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)


def _claim_rows() -> dict[str, tuple[str, str]]:
    return {display_id: (row.status, row.tier) for display_id, row in legacy_claim_rows().items()}


def _version_key(version: str, *, require_dev: bool = False) -> tuple[int, int, int, int, int]:
    match = VERSION_RE.fullmatch(version)
    assert match is not None, f'{version!r} is not a semver-like version'
    major, minor, patch, dev = match.groups()
    if require_dev:
        assert dev is not None, f'{version!r} is not a dev checkpoint version'
    return int(major), int(minor), int(patch), 0 if dev is None else 1, int(dev or 0)


def _registry_version() -> str:
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    return str(registry['repo']['version'])


def _previous_stable_version() -> str:
    major, minor, patch, *_ = _version_key(_registry_version(), require_dev=True)
    return f'{major}.{minor}.{max(patch - 1, 0)}'


def _package_version() -> str:
    project = tomllib.loads(PACKAGE_PYPROJECT.read_text(encoding='utf-8'))['project']
    return str(project['version'])


def test_post_promotion_handoff_validator_passes() -> None:
    result = _run('tools/ci/validate_post_promotion_handoff.py')
    assert result.returncode == 0, f'STDOUT\n{result.stdout}\nSTDERR\n{result.stderr}'


def test_next_line_and_next_target_claim_rows_exist() -> None:
    rows = legacy_claim_rows()
    for claim_id in REQUIRED:
        assert claim_id in rows
        assert is_claim_passing(rows[claim_id]), {claim_id: rows[claim_id].status}


def test_current_docs_record_active_dev_line_and_frozen_release_history() -> None:
    current_target = CURRENT_TARGET.read_text(encoding='utf-8')
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    adrs = {row['id']: row for row in registry['adrs']}
    governed_handoff_version = _registry_version()
    assert f'active next-line dev bundle: `docs/conformance/dev/{governed_handoff_version}/`' in current_target
    assert adrs['adr:1043']['status'] == 'accepted'
    assert adrs['adr:1044']['status'] == 'accepted'
    assert _version_key(_package_version()) >= _version_key(governed_handoff_version, require_dev=True)
