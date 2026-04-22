from __future__ import annotations

from pathlib import Path
import re

from common import repo_root, fail

ROOT = repo_root()
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
GATE_B_DOC = ROOT / 'docs' / 'conformance' / 'gates' / 'GATE_B_SURFACE_CLOSURE.md'

CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
ALLOWED_STATUSES = {'verified in checkpoint', 'implemented', 'de-scoped'}
GATE_B_CLAIMS = {
    'OAS-006',
    'RPC-002',
    'RPC-003',
    'OP-001',
    'OP-002',
    'OP-003',
    'OP-004',
    'OP-005',
    'OP-006',
    'OP-007',
    'OP-008',
    'OP-009',
    'OP-010',
    'OP-011',
    'OP-012',
    'CLI-001',
    'CLI-002',
    'GATE-007',
    'GATE-008',
}
REQUIRED_PATHS = [
    ROOT / 'docs' / 'developer' / 'CLI_REFERENCE.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'README.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'docs-ui.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'static-files.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'cookies-and-streaming.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'websockets-and-sse.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'forms-and-uploads.md',
    ROOT / 'docs' / 'developer' / 'operator' / 'middleware-catalog.md',
    ROOT / '.github' / 'workflows' / 'gate-b-surface-closure.yml',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'gate-results' / 'gate-b-surface-closure.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.17' / 'gate-results' / 'gate-b-surface-closure.md',
]


def parse_claim_rows() -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for match in CLAIM_ROW_RE.finditer(CLAIM_REGISTRY.read_text(encoding='utf-8')):
        claim_id, claim_text, status = match.groups()
        if claim_id in {'Claim ID', '---'}:
            continue
        rows[claim_id] = (claim_text.strip(), status.strip().lower())
    return rows


def main() -> None:
    errors: list[str] = []
    rows = parse_claim_rows()
    missing_claims = sorted(GATE_B_CLAIMS - set(rows))
    if missing_claims:
        errors.append(f'missing Gate B claim rows: {", ".join(missing_claims)}')

    for claim_id in sorted(GATE_B_CLAIMS & set(rows)):
        _claim_text, status = rows[claim_id]
        if status not in ALLOWED_STATUSES:
            errors.append(f'{claim_id} must be implemented, verified in checkpoint, or de-scoped (got {status!r})')

    current_target_text = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state_text = CURRENT_STATE.read_text(encoding='utf-8')
    gate_b_text = GATE_B_DOC.read_text(encoding='utf-8')

    if '## Current-target surfaces still missing\n\nNone.' not in current_target_text:
        errors.append('docs/conformance/CURRENT_TARGET.md must declare no current-target surfaces still missing')
    if 'no unresolved current-target surface gaps' not in current_state_text:
        errors.append('docs/conformance/CURRENT_STATE.md must declare that no unresolved current-target surface gaps remain')
    if 'Passed in the Gate B surface-closure checkpoint.' not in gate_b_text:
        errors.append('docs/conformance/gates/GATE_B_SURFACE_CLOSURE.md must record Gate B as passed in the Gate B surface-closure checkpoint')

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Gate B required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Gate B surface-closure validation passed')


if __name__ == '__main__':
    main()
