from __future__ import annotations

from common import repo_root, fail
from ssot_legacy_authority import assert_claims_passing, legacy_claim_rows, validate_claim_links

ROOT = repo_root()
DEV_INDEX = ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'EVIDENCE_INDEX.md'
REL_INDEX = ROOT / 'docs' / 'conformance' / 'releases' / '0.3.17' / 'EVIDENCE_INDEX.md'

RETAINED_CLAIMS = {
    'OAS-001', 'OAS-002', 'OAS-003', 'OAS-004', 'OAS-005', 'OAS-006',
    'SEC-001', 'SEC-002', 'SEC-003', 'SEC-004', 'SEC-005', 'SEC-006',
    'RPC-001', 'RPC-002', 'RPC-003',
    'RFC-7235', 'RFC-7617', 'RFC-6750',
}
DESCOPED_CLAIMS = {
    'OIDC-001', 'RFC-6749', 'RFC-7519', 'RFC-7636',
    'RFC-8414', 'RFC-8705', 'RFC-9110', 'RFC-9449',
}
GATE_C_INFRASTRUCTURE_CLAIMS = {'GATE-009', 'GATE-010'}
REQUIRED_PATHS = [
    ROOT / 'tools' / 'ci' / 'validate_gate_c_conformance_security.py',
    ROOT / 'tools' / 'ci' / 'tests' / 'test_gate_c_conformance_security.py',
    ROOT / '.github' / 'workflows' / 'gate-c-conformance-security.yml',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'gate-results' / 'gate-c-conformance-security.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.17' / 'gate-results' / 'gate-c-conformance-security.md',
    ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'p11-gate-c' / 'README.md',
]


def main() -> None:
    errors: list[str] = []
    rows = legacy_claim_rows()
    gate_c_claims = RETAINED_CLAIMS | DESCOPED_CLAIMS | GATE_C_INFRASTRUCTURE_CLAIMS
    errors.extend(assert_claims_passing(gate_c_claims, rows))
    errors.extend(validate_claim_links(gate_c_claims))

    dev_index_text = DEV_INDEX.read_text(encoding='utf-8')
    rel_index_text = REL_INDEX.read_text(encoding='utf-8')

    if '| Gate C | passed in Gate C conformance/security checkpoint |' not in dev_index_text:
        errors.append('dev evidence index must include the Gate C gate-result row')
    if 'gate-c-conformance-security.md' not in rel_index_text:
        errors.append('release evidence index must include the Gate C gate-result file')

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Gate C required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Gate C conformance/security validation passed')


if __name__ == '__main__':
    main()
