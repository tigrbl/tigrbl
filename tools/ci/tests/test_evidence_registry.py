from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / 'tools' / 'ci'))
sys.path.insert(0, str(REPO_ROOT / 'tools' / 'conformance'))

import build_phase9_evidence  # noqa: E402
from ssot_legacy_authority import evidence_registry_projection, legacy_claim_rows  # noqa: E402


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.run(
        [sys.executable, script],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def _claim_ids() -> set[str]:
    return set(legacy_claim_rows())


def test_ssot_legacy_claim_rows_are_covered_by_evidence_projection() -> None:
    data = evidence_registry_projection()
    claims = set(data['claims'])
    assert _claim_ids() <= claims


def test_evidence_registry_and_bundle_validators_pass() -> None:
    failures: list[str] = []
    for script in (
        'tools/ci/validate_evidence_registry.py',
        'tools/ci/validate_evidence_bundles.py',
    ):
        result = _run(script)
        if result.returncode != 0:
            failures.append(f"{script}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    assert not failures, '\n\n'.join(failures)


def test_phase9_evidence_generator_covers_current_claims_with_existing_paths() -> None:
    registry = build_phase9_evidence.build_registry()
    generated_claims = registry['claims']

    assert _claim_ids() <= set(generated_claims)

    missing: list[str] = []
    for claim_id, entry in generated_claims.items():
        for field in ('tests', 'artifact_paths', 'doc_paths'):
            for spec in entry[field]:
                path_part = spec.split('::', 1)[0].split('#', 1)[0]
                if not (REPO_ROOT / path_part).exists():
                    missing.append(f'{claim_id} {field}: {spec}')

    assert not missing, '\n'.join(missing)
