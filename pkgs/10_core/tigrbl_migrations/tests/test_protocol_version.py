from pathlib import Path

import tomllib

from tigrbl_migrations import MANIFEST_VERSION


def test_packaged_protocol_version_matches_pyproject_source() -> None:
    package = Path(__file__).parents[1]
    project = tomllib.loads((package / "pyproject.toml").read_text(encoding="utf-8"))
    resource = tomllib.loads(
        (package / "tigrbl_migrations/manifest_protocol.toml").read_text(encoding="utf-8")
    )
    assert project["tool"]["tigrbl"]["manifest"]["version"] == resource["version"]
    assert MANIFEST_VERSION == resource["version"]
