from importlib import import_module
from pathlib import Path
from shutil import copyfile

import pytest


def test_missing_contributor_link_fails_validation(tmp_path, monkeypatch, capsys):
    repo = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(repo / "tools" / "ci"))
    validator = import_module("validate_doc_pointers")
    for relative in [*validator.REQUIRED_CANONICAL_DOCS, Path("README.md")]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        copyfile(repo / relative, destination)

    (tmp_path / "CONTRIBUTING.md").write_text(
        "[Missing guide](docs/conformance/MISSING.md)\n", encoding="utf-8"
    )
    monkeypatch.setattr(validator, "ROOT", tmp_path)

    with pytest.raises(SystemExit) as failure:
        validator.main()

    assert failure.value.code == 1
    assert "CONTRIBUTING.md points to missing path docs/conformance/MISSING.md" in (
        capsys.readouterr().err
    )

