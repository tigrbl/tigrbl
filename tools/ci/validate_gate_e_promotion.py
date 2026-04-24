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
GATE_E_DOC = ROOT / 'docs' / 'conformance' / 'gates' / 'GATE_E_PROMOTION.md'
README = ROOT / 'README.md'
DOC_POINTERS = ROOT / 'docs' / 'governance' / 'DOC_POINTERS.md'
RELEASE_ROOT = ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18'
ARTIFACT_MANIFEST = RELEASE_ROOT / 'artifacts' / 'artifact-manifest.json'
CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
REQUIRED_PATHS = [
    ROOT / 'tools' / 'ci' / 'validate_gate_e_promotion.py',
    ROOT / 'tools' / 'ci' / 'tests' / 'test_gate_e_promotion.py',
    ROOT / '.github' / 'workflows' / 'gate-e-promotion.yml',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'RELEASE_NOTES.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'CLAIMS.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'EVIDENCE_INDEX.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'CURRENT_TARGET_SNAPSHOT.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'gate-results' / 'gate-e-promotion.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'gate-results' / 'gate-d-reproducibility.md',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'artifacts' / 'artifact-manifest.json',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'artifacts' / 'clean-room-package-manifest.json',
    ROOT / 'docs' / 'conformance' / 'releases' / '0.3.18' / 'artifacts' / 'installed-package-smoke-manifest.json',
    ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'p13-gate-e' / 'README.md',
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

    for claim_id in ('GATE-013', 'GATE-014', 'CERT-001', 'CERT-002'):
        if claim_id not in rows:
            errors.append(f'missing Gate E claim row: {claim_id}')

    for claim_id in ('CERT-001', 'CERT-002'):
        if claim_id in rows:
            _text, status, tier = rows[claim_id]
            if status != 'achieved':
                errors.append(f'{claim_id} must be achieved (got {status!r})')
            if not tier.lower().startswith('tier 3'):
                errors.append(f'{claim_id} must be Tier 3 (got {tier!r})')

    if 'GATE-013' in rows:
        _text, status, _tier = rows['GATE-013']
        if status not in {'verified in checkpoint', 'achieved'}:
            errors.append(f'GATE-013 must be verified in checkpoint or achieved (got {status!r})')
    if 'GATE-014' in rows:
        _text, status, _tier = rows['GATE-014']
        if status not in {'implemented', 'verified in checkpoint'}:
            errors.append(f'GATE-014 must be implemented or verified in checkpoint (got {status!r})')

    current_target_text = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state_text = CURRENT_STATE.read_text(encoding='utf-8')
    gate_model_text = GATE_MODEL.read_text(encoding='utf-8')
    gate_e_text = GATE_E_DOC.read_text(encoding='utf-8')
    readme_text = README.read_text(encoding='utf-8')
    pointer_text = DOC_POINTERS.read_text(encoding='utf-8')

    if '- Gate E status: passed in the Gate E promotion checkpoint' not in current_target_text:
        errors.append('docs/conformance/CURRENT_TARGET.md must record Gate E as passed in the Gate E promotion checkpoint')
    if 'Gate E: passed in the Gate E promotion checkpoint' not in current_state_text:
        errors.append('docs/conformance/CURRENT_STATE.md must record Gate E as passed in the Gate E promotion checkpoint')
    if 'Gate E is passed in the Gate E promotion checkpoint' not in gate_model_text:
        errors.append('docs/conformance/GATE_MODEL.md must record Gate E as passed in the Gate E promotion checkpoint')
    if 'Passed in the Gate E promotion checkpoint.' not in gate_e_text:
        errors.append('docs/conformance/gates/GATE_E_PROMOTION.md must record Gate E as passed in the Gate E promotion checkpoint')
    if '**Gate E promotion and release**' not in readme_text:
        errors.append('README.md must record the Gate E promotion checkpoint')
    if f'Current stable release bundle | `docs/conformance/releases/0.3.18/` |' not in pointer_text:
        errors.append('docs/governance/DOC_POINTERS.md must point to the promoted stable release bundle')

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Gate E required path: {path.relative_to(ROOT)}')

    if ARTIFACT_MANIFEST.exists():
        try:
            manifest = json.loads(ARTIFACT_MANIFEST.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            errors.append(f'Gate E artifact manifest must be valid JSON: {exc}')
        else:
            if manifest.get('release') != '0.3.18':
                errors.append('Gate E artifact manifest must record release 0.3.18')
            if manifest.get('source_dev_build') != '0.3.18.dev1':
                errors.append('Gate E artifact manifest must record source dev build 0.3.18.dev1')

    fail(errors)
    print('Gate E promotion validation passed')


if __name__ == '__main__':
    main()
