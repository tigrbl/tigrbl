from __future__ import annotations

import hashlib
import importlib.util
import sys

sys.dont_write_bytecode = True

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CI_ROOT = REPO_ROOT / 'tools' / 'ci'
if str(CI_ROOT) not in sys.path:
    sys.path.insert(0, str(CI_ROOT))

MODULE_PATH = CI_ROOT / 'validate_boundary_freeze_manifest.py'
spec = importlib.util.spec_from_file_location('validate_boundary_freeze_manifest', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_sha256_file_normalizes_windows_line_endings(tmp_path: Path) -> None:
    lf_path = tmp_path / 'freeze-manifest-lf.json'
    crlf_path = tmp_path / 'freeze-manifest-crlf.json'

    lf_bytes = b'{\n  "frozen": true\n}\n'
    lf_path.write_bytes(lf_bytes)
    crlf_path.write_bytes(lf_bytes.replace(b'\n', b'\r\n'))

    expected = hashlib.sha256(lf_bytes).hexdigest()

    assert module.sha256_file(lf_path) == expected
    assert module.sha256_file(crlf_path) == expected

