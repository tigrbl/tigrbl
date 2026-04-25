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
CLAIM_REGISTRY = REPO_ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = REPO_ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
NEXT_TARGETS = REPO_ROOT / 'docs' / 'conformance' / 'NEXT_TARGETS.md'
PACKAGE_PYPROJECT = REPO_ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
REGISTRY = REPO_ROOT / '.ssot' / 'registry.json'
REQUIRED = {'HANDOFF-001', 'HANDOFF-002', 'NEXT-001', 'NEXT-002'}
VERSION_RE = re.compile(r'^([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.dev([0-9]+))?$')


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
    governed_handoff_version = _registry_version()
    stable_handoff_version = _previous_stable_version()
    assert f'active next-line dev bundle: `docs/conformance/dev/{governed_handoff_version}/`' in current_target
    assert f'The active working tree is now `{governed_handoff_version}`.' in current_state
    assert f'Stable release `{stable_handoff_version}` is frozen as current-boundary release history.' in next_targets
    assert _version_key(_package_version()) >= _version_key(governed_handoff_version, require_dev=True)
