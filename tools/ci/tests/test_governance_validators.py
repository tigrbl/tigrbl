from __future__ import annotations

import os
import subprocess
import sys
sys.dont_write_bytecode = True
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

SCRIPTS = [
    'tools/ci/validate_package_layout.py',
    'tools/ci/validate_doc_pointers.py',
    'tools/ci/validate_root_clutter.py',
    'tools/ci/lint_claim_language.py',
    'tools/ci/validate_path_lengths.py',
    'tools/ci/validate_boundary_freeze_manifest.py',
    'tools/ci/lint_release_note_claims.py',
    'tools/ci/validate_evidence_registry.py',
    'tools/ci/validate_evidence_bundles.py',
    'tools/ci/validate_gate_b_surface_closure.py',
    'tools/ci/validate_gate_c_conformance_security.py',
    'tools/ci/validate_gate_d_reproducibility.py',
    'tools/ci/validate_gate_e_promotion.py',
    'tools/ci/validate_phase14_handoff.py',
]


def _run(script: str) -> subprocess.CompletedProcess[str]:
    import shutil
    cache = REPO_ROOT / '.pytest_cache'
    if cache.exists():
        shutil.rmtree(cache)
    for path in REPO_ROOT.rglob('__pycache__'):
        shutil.rmtree(path)
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


def test_repo_governance_scripts_pass() -> None:
    failures: list[str] = []
    for script in SCRIPTS:
        result = _run(script)
        if result.returncode != 0:
            failures.append(f"{script}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    assert not failures, '\n\n'.join(failures)
