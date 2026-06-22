from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.release import release_automation
from tools.release.release_automation import (
    Version,
    build_plan,
    ensure_allowed_target_version,
)


def test_python_patch_bump_always_targets_dev_release() -> None:
    assert str(Version.parse("0.3.19.dev1").bump("patch")) == "0.3.19.dev2"
    assert str(Version.parse("0.3.19").bump("patch")) == "0.3.20.dev1"


def test_python_finalize_converts_dev_to_release() -> None:
    assert str(Version.parse("0.3.19.dev1").bump("finalize")) == "0.3.19"


def test_python_bump_named_actions_map_to_expected_behavior() -> None:
    assert str(Version.parse("0.3.19").bump("minor")) == "0.4.0.dev1"
    assert str(Version.parse("0.3.19").bump("patch")) == "0.3.20.dev1"
    assert str(Version.parse("0.3.19").bump("dev")) == "0.3.20.dev1"
    assert str(Version.parse("0.3.19.dev1").bump("dev")) == "0.3.19.dev2"
    assert str(Version.parse("0.3.19").bump("x")) == "0.4.0.dev1"
    assert str(Version.parse("0.3.19").bump("y")) == "0.3.20.dev1"
    assert str(Version.parse("0.3.19").bump("z")) == "0.3.20.dev1"
    assert str(Version.parse("0.3.19.dev1").bump("z")) == "0.3.19.dev2"


def test_legacy_aliases_map_to_named_actions() -> None:
    assert str(Version.parse("0.3.19").bump("y")) == str(Version.parse("0.3.19").bump("patch"))
    assert str(Version.parse("0.3.19").bump("x")) == str(Version.parse("0.3.19").bump("minor"))
    assert str(Version.parse("0.3.19").bump("z")) == str(Version.parse("0.3.19").bump("dev"))


def test_w_major_bump_is_rejected() -> None:
    with pytest.raises(ValueError, match="disallowed"):
        Version.parse("0.3.19").bump("w")


def test_finalize_keeps_already_stable_versions() -> None:
    assert str(Version.parse("0.3.19").bump("finalize")) == "0.3.19"


def test_release_plan_uses_required_github_tag_shape() -> None:
    plan = build_plan("patch", write_changes=False)
    tags = [release["tag"] for release in plan["github_releases"]]
    tigrbl_release = next(
        release for release in plan["python"] if release["name"] == "tigrbl"
    )
    assert f"tigrbl=={tigrbl_release['version']}" in tags
    assert all("==" in tag for tag in tags)


def test_release_plan_can_select_one_python_package() -> None:
    plan = build_plan("patch", write_changes=False, packages="tigrbl")

    assert [release["name"] for release in plan["python"]] == ["tigrbl"]
    assert "crates" not in plan
    assert "crate_publish_order" not in plan
    assert [release["tag"] for release in plan["github_releases"]] == [
        f"tigrbl=={plan['python'][0]['version']}"
    ]
    assert plan["package_selection"] == ["tigrbl"]


def test_release_plan_can_select_package_subset() -> None:
    plan = build_plan(
        "patch",
        write_changes=False,
        packages="tigrbl",
    )

    assert [release["name"] for release in plan["python"]] == ["tigrbl"]
    assert "crates" not in plan
    assert "crate_publish_order" not in plan
    assert plan["package_selection"] == [
        "tigrbl",
    ]


def test_unknown_package_selection_fails() -> None:
    with pytest.raises(ValueError, match="unknown package"):
        build_plan("patch", write_changes=False, packages="does-not-exist")


def test_release_plan_rejects_downversioning() -> None:
    with pytest.raises(ValueError, match="downversion"):
        ensure_allowed_target_version("tigrbl", "0.4.0.dev2", "0.4.0.dev1")


def test_release_plan_rejects_versions_below_floor() -> None:
    with pytest.raises(ValueError, match="below the required floor"):
        ensure_allowed_target_version("tigrbl", "0.3.20.dev1", "0.3.20.dev2")


def test_create_github_releases_marks_dev_tags_as_prereleases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "release-plan.json"
    summary.write_text(
        json.dumps(
            {
                "semver": "patch",
                "prerelease": False,
                "github_releases": [
                    {
                        "name": "tigrbl",
                        "kind": "pypi",
                        "path": "pkgs/tigrbl/pyproject.toml",
                        "version": "0.3.20.dev1",
                        "tag": "tigrbl==0.3.20.dev1",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    run_calls: list[list[str]] = []

    class _Completed:
        def __init__(self, returncode: int, stdout: str = "") -> None:
            self.returncode = returncode
            self.stdout = stdout

    def fake_subprocess_run(args: list[str], **kwargs) -> _Completed:
        if args[:3] == ["gh", "release", "view"]:
            return _Completed(1)
        if args[:2] == ["git", "rev-list"]:
            return _Completed(0, stdout="c0ffee")
        if args[:2] == ["git", "rev-parse"]:
            return _Completed(1)
        if args[:2] == ["git", "config"]:
            return _Completed(0)
        return _Completed(0)

    monkeypatch.setattr(release_automation, "ensure_git_identity", lambda: None)
    monkeypatch.setattr(release_automation, "git_output", lambda args: "deadbeef")
    monkeypatch.setattr(release_automation, "run", lambda args, **kwargs: run_calls.append(args))
    monkeypatch.setattr(release_automation.subprocess, "run", fake_subprocess_run)

    release_automation.create_github_releases(summary)

    gh_release_commands = [
        call for call in run_calls if call[:3] == ["gh", "release", "create"]
    ]
    assert gh_release_commands, run_calls
    assert "--prerelease" in gh_release_commands[0]


def test_create_github_releases_rejects_existing_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "release-plan.json"
    summary.write_text(
        json.dumps(
            {
                "semver": "patch",
                "prerelease": True,
                "github_releases": [
                    {
                        "name": "tigrbl",
                        "kind": "pypi",
                        "path": "pkgs/tigrbl/pyproject.toml",
                        "version": "0.4.0.dev1",
                        "tag": "tigrbl==0.4.0.dev1",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    class _Completed:
        def __init__(self, returncode: int) -> None:
            self.returncode = returncode

    def fake_subprocess_run(args: list[str], **kwargs) -> _Completed:
        if args[:3] == ["gh", "release", "view"]:
            return _Completed(0)
        if args[:2] == ["git", "rev-parse"]:
            return _Completed(1)
        if args[:2] == ["git", "config"]:
            return _Completed(0)
        return _Completed(0)

    monkeypatch.setattr(release_automation, "ensure_git_identity", lambda: None)
    monkeypatch.setattr(release_automation, "git_output", lambda args: "deadbeef")
    monkeypatch.setattr(release_automation, "run", lambda args, **kwargs: None)
    monkeypatch.setattr(release_automation.subprocess, "run", fake_subprocess_run)

    with pytest.raises(RuntimeError, match="already exists"):
        release_automation.create_github_releases(summary)


def test_validate_release_targets_rejects_existing_pypi_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "release-plan.json"
    summary.write_text(
        json.dumps(
            {
                "python": [{"name": "tigrbl", "version": "0.4.0.dev1"}],
                "github_releases": [],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(release_automation, "url_exists", lambda url: True)

    with pytest.raises(SystemExit):
        release_automation.validate_release_targets(
            summary,
            github=False,
            pypi=True,
        )
