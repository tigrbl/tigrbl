from __future__ import annotations

from pathlib import Path
import re

from common import repo_root, fail

ROOT = repo_root()
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
CURRENT_TARGET = ROOT / 'docs' / 'conformance' / 'CURRENT_TARGET.md'
CURRENT_STATE = ROOT / 'docs' / 'conformance' / 'CURRENT_STATE.md'
GATE_MODEL = ROOT / 'docs' / 'conformance' / 'GATE_MODEL.md'
GATE_D_DOC = ROOT / 'docs' / 'conformance' / 'gates' / 'GATE_D_REPRODUCIBILITY.md'
DEV_INDEX = ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'EVIDENCE_INDEX.md'
BUILD_NOTES = ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'BUILD_NOTES.md'
CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.MULTILINE)
REQUIRED_CLAIMS = {'GATE-011', 'GATE-012'}
ALLOWED = {'verified in checkpoint', 'implemented'}
REQUIRED_PATHS = [
    ROOT / 'tools' / 'conformance' / 'clean_room_package_smoke.py',
    ROOT / 'tools' / 'conformance' / 'installed_package_smoke.py',
    ROOT / 'tools' / 'ci' / 'validate_gate_d_reproducibility.py',
    ROOT / 'tools' / 'ci' / 'tests' / 'test_gate_d_reproducibility.py',
    ROOT / '.github' / 'workflows' / 'gate-d-reproducibility.yml',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'gate-results' / 'gate-d-reproducibility.md',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'artifacts' / 'clean-room-package-manifest.json',
    ROOT / 'docs' / 'conformance' / 'dev' / '0.3.18.dev1' / 'artifacts' / 'installed-package-smoke-manifest.json',
    ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'p12-gate-d' / 'README.md',
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
    for claim_id in sorted(REQUIRED_CLAIMS):
        if claim_id not in rows:
            errors.append(f'missing Gate D claim row: {claim_id}')
            continue
        _text, status = rows[claim_id]
        if status not in ALLOWED:
            errors.append(f'{claim_id} must be implemented or verified in checkpoint (got {status!r})')

    current_target_text = CURRENT_TARGET.read_text(encoding='utf-8')
    current_state_text = CURRENT_STATE.read_text(encoding='utf-8')
    gate_model_text = GATE_MODEL.read_text(encoding='utf-8')
    gate_d_text = GATE_D_DOC.read_text(encoding='utf-8')
    dev_index_text = DEV_INDEX.read_text(encoding='utf-8')
    build_notes = BUILD_NOTES.read_text(encoding='utf-8')

    if '- Gate D status: passed in the Gate D reproducibility checkpoint' not in current_target_text:
        errors.append('docs/conformance/CURRENT_TARGET.md must record Gate D as passed in the Gate D reproducibility checkpoint')
    if 'clean-room evidence passes on the selected candidate build' not in current_state_text:
        errors.append('docs/conformance/CURRENT_STATE.md must declare clean-room evidence passes on the candidate build')
    if 'Gate D is passed at checkpoint quality and machine-checked in CI' not in gate_model_text:
        errors.append('docs/conformance/GATE_MODEL.md must record Gate D as passed at checkpoint quality')
    if 'Passed in the Gate D reproducibility checkpoint.' not in gate_d_text:
        errors.append('docs/conformance/gates/GATE_D_REPRODUCIBILITY.md must record Gate D as passed in the Gate D reproducibility checkpoint')
    if '| Gate D | passed in Gate D reproducibility checkpoint |' not in dev_index_text:
        errors.append('dev evidence index must include the Gate D gate-result row')
    if 'working tree package version is now `0.3.18.dev1`' not in build_notes:
        errors.append('build notes must record synchronized package metadata for 0.3.18.dev1')

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f'missing Gate D required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Gate D reproducibility validation passed')


if __name__ == '__main__':
    main()
