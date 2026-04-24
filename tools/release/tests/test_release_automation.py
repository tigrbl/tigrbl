from __future__ import annotations

from tools.release.release_automation import Version, build_plan


def test_python_patch_bump_always_targets_dev_release() -> None:
    assert str(Version.parse("0.3.19.dev1").bump("patch")) == "0.3.20.dev1"
    assert str(Version.parse("0.3.19").bump("patch")) == "0.3.20.dev1"


def test_python_finalize_converts_dev_to_release() -> None:
    assert str(Version.parse("0.3.19.dev1").bump("finalize")) == "0.3.19"


def test_cargo_dev_release_uses_semver_prerelease() -> None:
    assert str(Version.parse("0.1.0", cargo=True).bump("minor")) == "0.2.0-dev.1"
    assert str(Version.parse("0.2.0-dev.1", cargo=True).bump("finalize")) == "0.2.0"


def test_finalize_keeps_already_stable_versions() -> None:
    assert str(Version.parse("0.3.19").bump("finalize")) == "0.3.19"
    assert str(Version.parse("0.1.0", cargo=True).bump("finalize")) == "0.1.0"


def test_release_plan_uses_required_github_tag_shape() -> None:
    plan = build_plan("patch", write_changes=False)
    tags = [release["tag"] for release in plan["github_releases"]]
    assert "tigrbl==0.3.20.dev1" in tags
    assert "tigrbl_rs_spec==0.1.1-dev.1" in tags
    assert all("==" in tag for tag in tags)
