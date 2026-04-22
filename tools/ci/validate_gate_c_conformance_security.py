from __future__ import annotations

from pathlib import Path
import json
import re

from common import repo_root, fail

ROOT = repo_root()
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
GATE_MODEL = ROOT / 'docs' / 'conformance' / 'GATE_MODEL.md'
GATE_C_DOC = ROOT / 'docs' / 'conformance' / 'gates' / 'GATE_C_CONFORMANCE_SECURITY.md'
EVIDENCE_REGISTRY = ROOT / 'docs' / 'conformance' / 'EVIDENCE_REGISTRY.json'
DEV_INDEX = ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'EVIDENCE_INDEX.md'
REL_INDEX = ROOT / 'docs' / 'conformance' / 'releases' / '0.3.17' / 'EVIDENCE_INDEX.md'

CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)

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
RETAINED_ALLOWED = {'verified in checkpoint', 'implemented'}
REQUIRED_PATHS = [
    ROOT / 'tools' / 'ci' / 'validate_gate_c_conformance_security.py',
    ROOT / 'tools' / 'ci' / 'tests' / 'test_gate_c_conformance_security.py',
    ROOT / '.github' / 'workflows' / 'gate-c-conformance-security.yml',
    ROOT / 'docs' / 'conformance' / 'RFC_SECURITY_EVIDENCE_MAP.md',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'gate-results' / 'gate-c-conformance-security.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.17' / 'gate-results' / 'gate-c-conformance-security.md',
    ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'p11-gate-c' / 'README.md',
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
    evidence_registry = json.loads(EVIDENCE_REGISTRY.read_text(encoding='utf-8'))
    mapped_claims = set(evidence_registry.get('claims', {}))

    for claim_id in sorted(RETAINED_CLAIMS):
        if claim_id not in rows:
            errors.append(f'missing retained Gate C claim row: {claim_id}')
            continue
        _claim_text, status = rows[claim_id]
        if status not in RETAINED_ALLOWED:
            errors.append(f'{claim_id} must be implemented or verified in checkpoint (got {status!r})')
        if claim_id not in mapped_claims:
            errors.append(f'{claim_id} missing from docs/conformance/EVIDENCE_REGISTRY.json')

    for claim_id in sorted(DESCOPED_CLAIMS):
        if claim_id not in rows:
            errors.append(f'missing de-scoped Gate C claim row: {claim_id}')
            continue
        _claim_text, status = rows[claim_id]
        if not status.startswith('de-scoped'):
            errors.append(f'{claim_id} must remain explicitly de-scoped (got {status!r})')
        if claim_id not in mapped_claims:
            errors.append(f'{claim_id} missing from docs/conformance/EVIDENCE_REGISTRY.json')

    for claim_id in ('GATE-009', 'GATE-010'):
        if claim_id not in rows:
            errors.append(f'missing Gate C infrastructure claim row: {claim_id}')
        if claim_id not in mapped_claims:
            errors.append(f'{claim_id} missing from docs/conformance/EVIDENCE_REGISTRY.json')

    current_target_text = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state_text = CURRENT_STATE.read_text(encoding='utf-8')
    gate_model_text = GATE_MODEL.read_text(encoding='utf-8')
    gate_c_text = GATE_C_DOC.read_text(encoding='utf-8')
    dev_index_text = DEV_INDEX.read_text(encoding='utf-8')
    rel_index_text = REL_INDEX.read_text(encoding='utf-8')

    if '- Gate C status: passed in the Gate C conformance/security checkpoint' not in current_target_text:
        errors.append('docs/conformance/CURRENT_TARGET.md must record Gate C as passed in the Gate C conformance/security checkpoint')
    if 'no unresolved retained spec/security gaps remain' not in current_state_text:
        errors.append('docs/conformance/CURRENT_STATE.md must declare no unresolved retained spec/security gaps remain')
    if 'Gate C is passed at checkpoint quality and machine-checked in CI' not in gate_model_text:
        errors.append('docs/conformance/GATE_MODEL.md must record Gate C as passed at checkpoint quality')
    if 'Passed in the Gate C conformance/security checkpoint.' not in gate_c_text:
        errors.append('docs/conformance/gates/GATE_C_CONFORMANCE_SECURITY.md must record Gate C as passed in the Gate C conformance/security checkpoint')
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
