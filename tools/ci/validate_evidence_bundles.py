from __future__ import annotations

from pathlib import Path
from common import repo_root, fail

ROOT = repo_root()
DEV_ROOT = ROOT / 'docs' / 'conformance' / 'dev'
RELEASE_ROOT = ROOT / 'docs' / 'conformance' / 'releases'

REQUIRED_DEV_FILES = [
    'BUILD_NOTES.md',
    'EVIDENCE_INDEX.md',
    'CLAIMS.md',
]
REQUIRED_RELEASE_FILES = [
    'RELEASE_NOTES.md',
    'CLAIMS.md',
    'EVIDENCE_INDEX.md',
    'CURRENT_TARGET_SNAPSHOT.md',
]


def main() -> None:
    errors: list[str] = []

    dev_dirs = sorted(path for path in DEV_ROOT.glob('*') if path.is_dir())
    rel_dirs = sorted(path for path in RELEASE_ROOT.glob('*') if path.is_dir())

    if not dev_dirs:
        errors.append('docs/conformance/dev/ must contain at least one versioned dev bundle directory')
    if not rel_dirs:
        errors.append('docs/conformance/releases/ must contain at least one versioned release bundle directory')

    for bundle in dev_dirs:
        for name in REQUIRED_DEV_FILES:
            if not (bundle / name).exists():
                errors.append(f'{bundle.relative_to(ROOT)} missing {name}')
        if not (bundle / 'gate-results').is_dir():
            errors.append(f'{bundle.relative_to(ROOT)} missing gate-results/')

    for bundle in rel_dirs:
        for name in REQUIRED_RELEASE_FILES:
            if not (bundle / name).exists():
                errors.append(f'{bundle.relative_to(ROOT)} missing {name}')
        if not (bundle / 'gate-results').is_dir():
            errors.append(f'{bundle.relative_to(ROOT)} missing gate-results/')
        if not (bundle / 'artifacts').is_dir():
            errors.append(f'{bundle.relative_to(ROOT)} missing artifacts/')

    fail(errors)
    print('evidence bundle validation passed')


if __name__ == '__main__':
    main()
