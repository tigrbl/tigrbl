from __future__ import annotations

from pathlib import Path
import re

from common import repo_root, fail

ROOT = repo_root()
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
NEXT_TARGETS = ROOT / 'docs' / 'conformance' / 'NEXT_TARGETS.md'
DOC_POINTERS = ROOT / 'docs' / 'governance' / 'DOC_POINTERS.md'
VERSIONING = ROOT / 'docs' / 'governance' / 'VERSIONING_POLICY.md'
PACKAGE_PYPROJECT = ROOT / 'pkgs' / 'core' / 'tigrbl' / 'pyproject.toml'
CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
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
    pyproject_text = PACKAGE_PYPROJECT.read_text(encoding='utf-8')

    if 'active next-line dev bundle: `docs/conformance/dev/0.3.19.dev1/`' not in current_target_text:
        errors.append('CURRENT_TARGET.md must record the active next-line dev bundle')
    if 'The active working tree is now `0.3.19.dev1`.' not in current_state_text:
        errors.append('CURRENT_STATE.md must record the active working-tree version 0.3.19.dev1')
    if 'Stable release `0.3.18` is frozen as current-boundary release history.' not in next_targets_text:
        errors.append('NEXT_TARGETS.md must record frozen stable release history')
    if '`DataTypeSpec`' not in next_targets_text or '`TypeAdapter`' not in next_targets_text or '`EngineDatatypeBridge`' not in next_targets_text:
        errors.append('NEXT_TARGETS.md must record the datatype semantic-center and engine bridge scope')
    if 'docs/conformance/NEXT_TARGETS.md' not in pointer_text:
        errors.append('DOC_POINTERS.md must include NEXT_TARGETS.md')
    if 'docs/conformance/dev/0.3.19.dev1/' not in pointer_text:
        errors.append('DOC_POINTERS.md must include the active dev bundle path')
    if 'Post-promotion handoff has now opened the next governed development line as `0.3.19.dev1`.' not in versioning_text:
        errors.append('VERSIONING_POLICY.md must record the active next governed line')
    if 'version = "0.3.19.dev1"' not in pyproject_text:
        errors.append('pkgs/core/tigrbl/pyproject.toml must record version 0.3.19.dev1')

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Post-promotion handoff required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Post-promotion handoff validation passed')


if __name__ == '__main__':
    main()
