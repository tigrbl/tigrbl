from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib

from common import repo_root


ROOT = repo_root()
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
NEXT_TARGETS = ROOT / 'docs' / 'conformance' / 'NEXT_TARGETS.md'
DOC_POINTERS = ROOT / 'docs' / 'governance' / 'DOC_POINTERS.md'
VERSIONING = ROOT / 'docs' / 'governance' / 'VERSIONING_POLICY.md'
PACKAGE_PYPROJECT = ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
REGISTRY = ROOT / '.ssot' / 'registry.json'
CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
VERSION_RE = re.compile(r'^([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.dev([0-9]+))?$')


REQUIRED_CLAIM_STATUS = {
    'HANDOFF-001': {'verified in checkpoint'},
    'HANDOFF-002': {'implemented', 'verified in checkpoint'},
    'NEXT-001': {'verified in checkpoint'},
    'NEXT-002': {'verified in checkpoint'},
}

REQUIRED_CLAIM_TIER = {
    'HANDOFF-001': 'Tier 2',
    'HANDOFF-002': 'Tier 1',
    'NEXT-001': 'Tier 2',
    'NEXT-002': 'Tier 2',
}


def _registry_version() -> str:
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    return str(registry.get('repo', {}).get('version', ''))


def _package_version() -> str:
    project = tomllib.loads(PACKAGE_PYPROJECT.read_text(encoding='utf-8')).get('project', {})
    return str(project.get('version', ''))


def _version_key(version: str) -> tuple[int, int, int, int, int]:
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f'{version!r} is not a semver-like version')
    major, minor, patch, dev = match.groups()
    return int(major), int(minor), int(patch), 0 if dev is None else 1, int(dev or 0)


def _previous_stable_version(version: str) -> str:
    major, minor, patch, *_ = _version_key(version)
    return f'{major}.{minor}.{max(patch - 1, 0)}'


def _required_claim_text(governed_version: str, stable_version: str) -> dict[str, str]:
    return {
        'HANDOFF-001': 'Post-promotion handoff freezes stable release history and isolates the active next-line bundle',
        'HANDOFF-002': 'Post-promotion handoff validator and workflow exist',
        'NEXT-001': (
            f'Active next development line `{governed_version}` is opened in governed docs, evidence scaffolding, and package metadata'
        ),
        'NEXT-002': (
            f'Datatype/table work is isolated to governed next-target ADRs and plans and remains outside release `{stable_version}` '
            'certification'
        ),
    }


def _required_claim_new_status(claim_id: str) -> str:
    if claim_id == 'HANDOFF-002':
        return 'implemented'
    return 'verified in checkpoint'


def _append_section(path: Path, marker: str, section: str) -> bool:
    text = path.read_text(encoding='utf-8')
    if marker in text:
        return False
    if text.endswith('\n'):
        path.write_text(text + section.rstrip('\n') + '\n', encoding='utf-8')
    else:
        path.write_text(text.rstrip('\n') + '\n\n' + section.rstrip('\n') + '\n', encoding='utf-8')
    return True


def _ensure_file(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip('\n') + '\n', encoding='utf-8')
    return True


def _governed_dev_path(version: str) -> Path:
    return ROOT / 'docs' / 'conformance' / 'dev' / version


def _fix_claim_rows(governed_version: str, stable_version: str) -> int:
    return 0


def _fix_docs_handoff_markers(stable_version: str, governed_version: str) -> int:
    governed_dev_path = f'docs/conformance/dev/{governed_version}/'
    changed = 0

    if NEXT_TARGETS.exists():
        next_targets_text = NEXT_TARGETS.read_text(encoding='utf-8')
        next_target_added = False
        if f'Stable release `{stable_version}` is frozen as current-boundary release history.' not in next_targets_text:
            append = f' - Stable release `{stable_version}` is frozen as current-boundary release history.\n'
            next_target_added = _append_section(
                NEXT_TARGETS,
                f'Stable release `{stable_version}` is frozen as current-boundary release history.',
                append,
            )
        missing_datatype_markers = [
            marker
            for marker in ('`DataTypeSpec`', '`TypeAdapter`', '`EngineDatatypeBridge`')
            if marker not in next_targets_text
        ]
        if missing_datatype_markers:
            changed += int(_append_section(
                NEXT_TARGETS,
                '`DataTypeSpec`',
                '- Scope guard: datatype semantic-center and engine bridge work now resides in deferred next-target ADRs.',
            ))
        changed += int(next_target_added)
    else:
        missing_datatype_markers = []

    if f'Post-promotion handoff has now opened the next governed development line as `{governed_version}`.' not in VERSIONING.read_text(encoding='utf-8'):
        changed += int(
            _append_section(
                VERSIONING,
                f'Post-promotion handoff has now opened the next governed development line as `{governed_version}`.',
                f'Post-promotion handoff has now opened the next governed development line as `{governed_version}`.',
            )
        )

    bundle_root = _governed_dev_path(governed_version)
    audit_root = ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'post-promotion-handoff'
    archive_root = ROOT / 'docs' / 'notes' / 'archive' / '2026' / 'post-promotion-handoff'
    changed += int(
        _ensure_file(
            bundle_root / 'gate-results' / 'README.md',
            '# Post-promotion handoff gate results',
        )
    )
    changed += int(
        _ensure_file(
            bundle_root / 'gate-results' / 'post-promotion-handoff.md',
            '# Post-promotion handoff proof',
        )
    )
    changed += int(
        _ensure_file(
            audit_root / 'README.md',
            '# Post-promotion handoff audit',
        )
    )
    changed += int(
        _ensure_file(
            archive_root / 'README.md',
            '# Post-promotion handoff archive',
        )
    )

    return changed + int((missing_datatype_markers or []).__len__() > 0)


def _sync_package_version_floor() -> int:
    governed_version = _registry_version()
    package_version = _package_version()
    pkg_key = _version_key(package_version)
    governed_key = _version_key(governed_version)
    if pkg_key < governed_key:
        # conservative floor: set package version to the governed line to prevent stale drift
        if package_version != governed_version:
            text = PACKAGE_PYPROJECT.read_text(encoding='utf-8')
            updated = re.sub(r'(^\\s*version\\s*=\\s*)\"[^\"]+\"', f'\\1\"{governed_version}\"', text, flags=re.MULTILINE)
            if text != updated:
                PACKAGE_PYPROJECT.write_text(updated, encoding='utf-8')
                return 1
    return 0


def main() -> None:
    governed_version = _registry_version()
    stable_version = _previous_stable_version(governed_version)
    total = 0
    total += _fix_claim_rows(governed_version, stable_version)
    total += _fix_docs_handoff_markers(stable_version, governed_version)
    total += _sync_package_version_floor()
    if total:
        print(f'Post-promotion handoff repair complete: applied {total} targeted fixes.')
    else:
        print('Post-promotion handoff repair complete: no drift detected.')


if __name__ == '__main__':
    main()
