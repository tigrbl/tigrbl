from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib

from common import repo_root, fail

ROOT = repo_root()
REGISTRY = ROOT / '.ssot' / 'registry.json'
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
NEXT_TARGETS = ROOT / 'docs' / 'conformance' / 'NEXT_TARGETS.md'
DOC_POINTERS = ROOT / 'docs' / 'governance' / 'DOC_POINTERS.md'
VERSIONING = ROOT / 'docs' / 'governance' / 'VERSIONING_POLICY.md'
PACKAGE_PYPROJECT = ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
DEV_VERSION_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.dev(\d+)$')
REQUIRED_PATHS = [
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.19.dev1' / 'BUILD_NOTES.md',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.19.dev1' / 'CLAIMS.md',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.19.dev1' / 'EVIDENCE_INDEX.md',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.19.dev1' / 'gate-results' / 'README.md',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.19.dev1' / 'gate-results' / 'post-promotion-handoff.md',
    ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'post-promotion-handoff' / 'README.md',
    ROOT / 'docs' / 'notes' / 'archive' / '2026' / 'post-promotion-handoff' / 'README.md',
    ROOT / '.ssot' / 'adr' / 'ADR-1043-post-promotion-release-history-freeze.yaml',
    ROOT / '.ssot' / 'adr' / 'ADR-1044-next-target-datatype-table-program-activation.yaml',
    ROOT / 'tools' / 'ci' / 'validate_post_promotion_handoff.py',
    ROOT / 'tools' / 'ci' / 'tests' / 'test_post_promotion_handoff.py',
    ROOT / '.github' / 'workflows' / 'post-promotion-handoff.yml',
]


def _dev_version_key(version: str) -> tuple[int, int, int, int] | None:
    match = DEV_VERSION_RE.fullmatch(version)
    if not match:
        return None
    major, minor, patch, dev = match.groups()
    return int(major), int(minor), int(patch), int(dev)


def _registry_version() -> str:
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    return str(registry.get('repo', {}).get('version', ''))


def _package_version() -> str:
    project = tomllib.loads(PACKAGE_PYPROJECT.read_text(encoding='utf-8')).get('project', {})
    return str(project.get('version', ''))


def parse_claim_rows() -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    for match in CLAIM_ROW_RE.finditer(CLAIM_REGISTRY.read_text(encoding='utf-8')):
        claim_id, claim_text, status, tier = match.groups()
        if claim_id in {'Claim ID', '---'}:
            continue
        rows[claim_id] = (claim_text.strip(), status.strip().lower(), tier.strip())
    return rows


def main() -> None:
    errors: list[str] = []
    rows = parse_claim_rows()
    governed_dev_version = _registry_version()
    package_version = _package_version()

    required_status = {
        'HANDOFF-001': {'verified in checkpoint'},
        'HANDOFF-002': {'implemented', 'verified in checkpoint'},
        'NEXT-001': {'verified in checkpoint'},
        'NEXT-002': {'verified in checkpoint'},
    }
    for claim_id, allowed in required_status.items():
        if claim_id not in rows:
            errors.append(f'missing Post-promotion handoff claim row: {claim_id}')
            continue
        _text, status, _tier = rows[claim_id]
        if status not in allowed:
            errors.append(f'{claim_id} has unexpected status {status!r}')

    current_target_text = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state_text = CURRENT_STATE.read_text(encoding='utf-8')
    next_targets_text = NEXT_TARGETS.read_text(encoding='utf-8')
    pointer_text = DOC_POINTERS.read_text(encoding='utf-8')
    versioning_text = VERSIONING.read_text(encoding='utf-8')
    governed_dev_path = f'docs/conformance/dev/{governed_dev_version}/'

    if f'active next-line dev bundle: `{governed_dev_path}`' not in current_target_text:
        errors.append('CURRENT_TARGET.md must record the active next-line dev bundle')
    if f'The active working tree is now `{governed_dev_version}`.' not in current_state_text:
        errors.append(f'CURRENT_STATE.md must record the governed handoff version {governed_dev_version}')
    if 'Stable release `0.3.18` is frozen as current-boundary release history.' not in next_targets_text:
        errors.append('NEXT_TARGETS.md must record frozen stable release history')
    if '`DataTypeSpec`' not in next_targets_text or '`TypeAdapter`' not in next_targets_text or '`EngineDatatypeBridge`' not in next_targets_text:
        errors.append('NEXT_TARGETS.md must record the datatype semantic-center and engine bridge scope')
    if 'docs/conformance/NEXT_TARGETS.md' not in pointer_text:
        errors.append('DOC_POINTERS.md must include NEXT_TARGETS.md')
    if governed_dev_path not in pointer_text:
        errors.append('DOC_POINTERS.md must include the active dev bundle path')
    if f'Post-promotion handoff has now opened the next governed development line as `{governed_dev_version}`.' not in versioning_text:
        errors.append('VERSIONING_POLICY.md must record the active next governed line')
    governed_key = _dev_version_key(governed_dev_version)
    package_key = _dev_version_key(package_version)
    if governed_key is None:
        errors.append(f'.ssot/registry.json repo.version must be a dev checkpoint version, got {governed_dev_version!r}')
    elif package_key is None:
        errors.append(f'pkgs/core/tigrbl/pyproject.toml must record a dev checkpoint version, got {package_version!r}')
    elif package_key < governed_key:
        errors.append(
            'pkgs/core/tigrbl/pyproject.toml must not lag behind '
            f'.ssot/registry.json repo.version {governed_dev_version}; got {package_version}'
        )

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Post-promotion handoff required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Post-promotion handoff validation passed')


if __name__ == '__main__':
    main()
