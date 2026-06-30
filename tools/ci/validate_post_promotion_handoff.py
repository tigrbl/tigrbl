from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib

from common import repo_root, fail
from release_identity import parse_semver
from ssot_legacy_authority import assert_claims_passing, by_id, legacy_claim_rows, load_registry, path_spec_exists, validate_claim_links

ROOT = repo_root()
REGISTRY = ROOT / '.ssot' / 'registry.json'
DOC_POINTERS = ROOT / 'docs' / 'governance' / 'DOC_POINTERS.md'
VERSIONING = ROOT / 'docs' / 'governance' / 'VERSIONING_POLICY.md'
PACKAGE_PYPROJECT = ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
REQUIRED_ADRS = {'adr:1043', 'adr:1044'}
STATIC_REQUIRED_PATHS = [
    ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'post-promotion-handoff' / 'README.md',
    ROOT / 'docs' / 'notes' / 'archive' / '2026' / 'post-promotion-handoff' / 'README.md',
    ROOT / '.ssot' / 'adr' / 'ADR-1043-post-promotion-release-history-freeze.yaml',
    ROOT / '.ssot' / 'adr' / 'ADR-1044-next-target-datatype-table-program-activation.yaml',
    ROOT / 'tools' / 'ci' / 'validate_post_promotion_handoff.py',
    ROOT / 'tools' / 'ci' / 'tests' / 'test_post_promotion_handoff.py',
    ROOT / '.github' / 'workflows' / 'post-promotion-handoff.yml',
]


def _version_key(version: str, *, require_dev: bool = False) -> tuple[int, int, int, int, int] | None:
    try:
        return parse_semver(version, require_dev=require_dev)
    except ValueError:
        return None


def _required_paths(version: str) -> list[Path]:
    dev_root = ROOT / 'docs' / 'conformance' / 'dev' / version
    return [
        dev_root / 'BUILD_NOTES.md',
        dev_root / 'CLAIMS.md',
        dev_root / 'EVIDENCE_INDEX.md',
        dev_root / 'gate-results' / 'README.md',
        dev_root / 'gate-results' / 'post-promotion-handoff.md',
        *STATIC_REQUIRED_PATHS,
    ]


def _registry_version() -> str:
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    return str(registry.get('repo', {}).get('version', ''))


def _package_version() -> str:
    project = tomllib.loads(PACKAGE_PYPROJECT.read_text(encoding='utf-8')).get('project', {})
    return str(project.get('version', ''))


def main() -> None:
    errors: list[str] = []
    registry = load_registry()
    rows = legacy_claim_rows()
    governed_dev_version = _registry_version()
    package_version = _package_version()

    required_claims = {'HANDOFF-001', 'HANDOFF-002', 'NEXT-001', 'NEXT-002'}
    errors.extend(assert_claims_passing(required_claims, rows))
    errors.extend(validate_claim_links(required_claims))

    pointer_text = DOC_POINTERS.read_text(encoding='utf-8')
    versioning_text = VERSIONING.read_text(encoding='utf-8')

    adrs = by_id(registry, 'adrs')
    for adr_id in sorted(REQUIRED_ADRS):
        adr = adrs.get(adr_id)
        if adr is None:
            errors.append(f'missing post-promotion handoff ADR row: {adr_id}')
            continue
        if adr.get('status') != 'accepted':
            errors.append(f'{adr_id} must be accepted (got {adr.get("status")!r})')
        path = str(adr.get('path', '')).strip()
        if not path or not path_spec_exists(path):
            errors.append(f'{adr_id} references missing path: {path}')
    for marker in ('.ssot/registry.json', '.ssot/adr/', '.ssot/specs/', 'docs/conformance/dev/'):
        if marker not in pointer_text:
            errors.append(f'DOC_POINTERS.md must include {marker}')
    if f'Post-promotion handoff has now opened the next governed development line as `{governed_dev_version}`.' not in versioning_text:
        errors.append('VERSIONING_POLICY.md must record the active next governed line')
    governed_key = _version_key(governed_dev_version, require_dev=True)
    package_key = _version_key(package_version)
    if governed_key is None:
        errors.append(f'.ssot/registry.json repo.version must be a dev checkpoint version, got {governed_dev_version!r}')
    elif package_key is None:
        errors.append(f'pkgs/80_facade/tigrbl/pyproject.toml must record a valid semver, got {package_version!r}')
    elif package_key < governed_key:
        errors.append(
            'pkgs/80_facade/tigrbl/pyproject.toml must not lag behind '
            f'.ssot/registry.json repo.version {governed_dev_version}; got {package_version}'
        )

    for path in _required_paths(governed_dev_version):
        if not path.exists():
            errors.append(f'missing Post-promotion handoff required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Post-promotion handoff validation passed')


if __name__ == '__main__':
    main()
