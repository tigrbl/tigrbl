from __future__ import annotations

from common import repo_root, fail
from release_identity import promotion_source_dev_root, promotion_source_dev_version
from ssot_legacy_authority import assert_claims_passing, legacy_claim_rows, validate_claim_links

ROOT = repo_root()
REQUIRED_CLAIMS = {'GATE-011', 'GATE-012'}


def main() -> None:
    errors: list[str] = []
    rows = legacy_claim_rows()
    source_dev_version = promotion_source_dev_version()
    source_dev_root = promotion_source_dev_root()
    dev_index = source_dev_root / 'EVIDENCE_INDEX.md'
    build_notes_path = source_dev_root / 'BUILD_NOTES.md'
    required_paths = [
        ROOT / 'tools' / 'conformance' / 'clean_room_package_smoke.py',
        ROOT / 'tools' / 'conformance' / 'installed_package_smoke.py',
        ROOT / 'tools' / 'ci' / 'validate_gate_d_reproducibility.py',
        ROOT / 'tools' / 'ci' / 'tests' / 'test_gate_d_reproducibility.py',
        ROOT / '.github' / 'workflows' / 'gate-d-reproducibility.yml',
        source_dev_root / 'gate-results' / 'gate-d-reproducibility.md',
        source_dev_root / 'artifacts' / 'clean-room-package-manifest.json',
        source_dev_root / 'artifacts' / 'installed-package-smoke-manifest.json',
        ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'p12-gate-d' / 'README.md',
    ]
    errors.extend(assert_claims_passing(REQUIRED_CLAIMS, rows))
    errors.extend(validate_claim_links(REQUIRED_CLAIMS))

    dev_index_text = dev_index.read_text(encoding='utf-8')
    build_notes = build_notes_path.read_text(encoding='utf-8')

    if '| Gate D | passed in Gate D reproducibility checkpoint |' not in dev_index_text:
        errors.append('dev evidence index must include the Gate D gate-result row')
    if f'working tree package version is now `{source_dev_version}`' not in build_notes:
        errors.append(f'build notes must record synchronized package metadata for {source_dev_version}')

    for path in required_paths:
        if not path.exists():
            errors.append(f'missing Gate D required path: {path.relative_to(ROOT)}')

    fail(errors)
    print('Gate D reproducibility validation passed')


if __name__ == '__main__':
    main()
