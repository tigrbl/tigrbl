from __future__ import annotations

from pathlib import Path
import json
import re

from common import repo_root, fail

ROOT = repo_root()
CLAIM_REGISTRY = ROOT / 'docs' / 'conformance' / 'CLAIM_REGISTRY.md'
EVIDENCE_REGISTRY = ROOT / 'docs' / 'conformance' / 'EVIDENCE_REGISTRY.json'
CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|')


def parse_claim_ids() -> list[str]:
    ids: list[str] = []
    for line in CLAIM_REGISTRY.read_text(encoding='utf-8').splitlines():
        match = CLAIM_ROW_RE.match(line)
        if not match:
            continue
        claim_id = match.group(1).strip()
        if claim_id in {'Claim ID', '---'}:
            continue
        if re.match(r'^(?:[A-Z]+-\d+|RFC-\d+|OIDC-\d+)$', claim_id):
            ids.append(claim_id)
    return ids


def test_path_exists(spec: str) -> bool:
    path_part = spec.split('::', 1)[0].split('#', 1)[0]
    return (ROOT / path_part).exists()


def main() -> None:
    errors: list[str] = []
    claim_ids = set(parse_claim_ids())
    data = json.loads(EVIDENCE_REGISTRY.read_text(encoding='utf-8'))
    claims = data.get('claims', {})
    if not isinstance(claims, dict):
        errors.append('docs/conformance/EVIDENCE_REGISTRY.json must contain a top-level object key "claims"')
        fail(errors)
        return

    mapped_ids = set(claims)
    missing = sorted(claim_ids - mapped_ids)
    extra = sorted(mapped_ids - claim_ids)
    if missing:
        errors.append(f'evidence registry missing claim ids: {", ".join(missing)}')
    if extra:
        errors.append(f'evidence registry contains unknown claim ids: {", ".join(extra)}')

    for claim_id in sorted(claim_ids & mapped_ids):
        entry = claims[claim_id]
        if not isinstance(entry, dict):
            errors.append(f'{claim_id} evidence entry must be an object')
            continue
        for field in ('tests', 'ci_jobs', 'artifact_paths', 'doc_paths', 'lane_classes'):
            value = entry.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f'{claim_id} must declare non-empty {field}')
                continue
            for item in value:
                if not isinstance(item, str) or not item.strip():
                    errors.append(f'{claim_id} has invalid {field} entry: {item!r}')
                elif field in {'tests', 'ci_jobs', 'artifact_paths', 'doc_paths'} and not test_path_exists(item):
                    errors.append(f'{claim_id} references missing path in {field}: {item}')

    fail(errors)
    print('evidence registry validation passed')


if __name__ == '__main__':
    main()
