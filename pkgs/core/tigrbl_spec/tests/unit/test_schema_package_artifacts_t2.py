from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from tarfile import TarFile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[5]


def test_built_wheel_and_sdist_contain_schema_migration_and_model_artifacts() -> None:
    tmp_root = ROOT / ".tmp"
    tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp_root) as build_dir:
        out_dir = Path(build_dir)
        subprocess.run(
            [
                "uv",
                "build",
                "--package",
                "tigrbl_spec",
                "--no-build-isolation",
                "--out-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        wheel = next(out_dir.glob("tigrbl_spec-*.whl"))
        sdist = next(out_dir.glob("tigrbl_spec-*.tar.gz"))

        expected = [
            "tigrbl_spec/schemas/0.3.20/manifest.json",
            "tigrbl_spec/schemas/0.3.20/bundle.json",
            "tigrbl_spec/schemas/0.3.20/AppSpec.json",
            "tigrbl_spec/migrations/__init__.py",
            "tigrbl_spec/models/v0_3_20/__init__.py",
        ]

        with ZipFile(wheel) as archive:
            wheel_names = set(archive.namelist())
        assert set(expected).issubset(wheel_names)

        with TarFile.open(sdist) as archive:
            sdist_names = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
        assert set(expected).issubset(sdist_names)
