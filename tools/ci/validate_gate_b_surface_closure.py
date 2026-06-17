from __future__ import annotations

from common import repo_root, fail
from ssot_legacy_authority import assert_claims_passing, legacy_claim_rows, validate_claim_links

ROOT = repo_root()

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


def main() -> None:
    errors: list[str] = []
    rows = legacy_claim_rows()
    errors.extend(assert_claims_passing(GATE_B_CLAIMS, rows))
    errors.extend(validate_claim_links(GATE_B_CLAIMS))

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Gate B required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Gate B surface-closure validation passed')


if __name__ == '__main__':
    main()
