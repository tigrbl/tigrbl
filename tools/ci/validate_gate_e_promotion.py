from __future__ import annotations

import json

from common import repo_root, fail
from release_identity import current_stable_release_root, current_stable_release_version, promotion_source_dev_version
from ssot_legacy_authority import assert_claims_passing, legacy_claim_rows, validate_claim_links

ROOT = repo_root()
README = ROOT / 'README.md'
DOC_POINTERS = ROOT / 'docs' / 'governance' / 'DOC_POINTERS.md'
REQUIRED_CLAIMS = {'GATE-013', 'GATE-014', 'CERT-001', 'CERT-002'}


def _is_t3(tier: str) -> bool:
    normalized = tier.lower().replace(' ', '')
    return normalized.startswith('t3') or normalized.startswith('tier3')


def main() -> None:
    errors: list[str] = []
    rows = legacy_claim_rows()
    stable_release_version = current_stable_release_version()
    source_dev_version = promotion_source_dev_version()
    release_root = current_stable_release_root()
    artifact_manifest = release_root / 'artifacts' / 'artifact-manifest.json'
    required_paths = [
        ROOT / 'tools' / 'ci' / 'validate_gate_e_promotion.py',
        ROOT / 'tools' / 'ci' / 'tests' / 'test_gate_e_promotion.py',
        ROOT / '.github' / 'workflows' / 'gate-e-promotion.yml',
        release_root / 'RELEASE_NOTES.md',
        release_root / 'CLAIMS.md',
        release_root / 'EVIDENCE_INDEX.md',
        release_root / 'CURRENT_TARGET_SNAPSHOT.md',
        release_root / 'gate-results' / 'gate-e-promotion.md',
        release_root / 'gate-results' / 'gate-d-reproducibility.md',
        release_root / 'artifacts' / 'artifact-manifest.json',
        release_root / 'artifacts' / 'clean-room-package-manifest.json',
        release_root / 'artifacts' / 'installed-package-smoke-manifest.json',
        ROOT / 'docs' / 'conformance' / 'audit' / '2026' / 'p13-gate-e' / 'README.md',
    ]

    errors.extend(assert_claims_passing(REQUIRED_CLAIMS, rows))
    errors.extend(validate_claim_links(REQUIRED_CLAIMS))
    for claim_id in ('CERT-001', 'CERT-002'):
        row = rows.get(claim_id)
        if row is not None and not _is_t3(row.tier):
            errors.append(f'{claim_id} must be T3 in SSOT (got {row.tier!r})')

    readme_text = README.read_text(encoding='utf-8')
    pointer_text = DOC_POINTERS.read_text(encoding='utf-8')

    if 'docs/conformance/releases/' not in readme_text or 'docs/conformance/dev/' not in readme_text:
        errors.append('README.md must point readers to release and dev conformance evidence roots')
    for marker in ('.ssot/registry.json', '.ssot/releases/', 'docs/conformance/releases/'):
        if marker not in pointer_text:
            errors.append(f'docs/governance/DOC_POINTERS.md must point to {marker}')

    for path in required_paths:
        if not path.exists():
            errors.append(f'missing Gate E required path: {path.relative_to(ROOT)}')

    if artifact_manifest.exists():
        try:
            manifest = json.loads(artifact_manifest.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            errors.append(f'Gate E artifact manifest must be valid JSON: {exc}')
        else:
            if manifest.get('release') != stable_release_version:
                errors.append(f'Gate E artifact manifest must record release {stable_release_version}')
            if manifest.get('source_dev_build') != source_dev_version:
                errors.append(f'Gate E artifact manifest must record source dev build {source_dev_version}')

    fail(errors)
    print('Gate E promotion validation passed')


if __name__ == '__main__':
    main()
