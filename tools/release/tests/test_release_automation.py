from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.release import release_automation
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
    assert "tigrbl_rs_spec==0.1.2-dev.1" in tags
    assert all("==" in tag for tag in tags)


def test_release_plan_can_select_one_python_package() -> None:
    plan = build_plan("patch", write_changes=False, packages="tigrbl_acme_ca")

    assert [release["name"] for release in plan["python"]] == ["tigrbl_acme_ca"]
    assert plan["crates"] == []
    assert plan["crate_publish_order"] == []
    assert [release["tag"] for release in plan["github_releases"]] == [
        "tigrbl_acme_ca==0.1.3.dev1"
    ]
    assert plan["package_selection"] == ["tigrbl_acme_ca"]


def test_release_plan_can_select_package_subset() -> None:
    plan = build_plan(
        "patch",
        write_changes=False,
        packages="tigrbl_acme_ca,tigrbl_rs_spec tigrbl_rs_ports",
    )

    assert [release["name"] for release in plan["python"]] == ["tigrbl_acme_ca"]
    assert [release["name"] for release in plan["crates"]] == [
        "tigrbl_rs_spec",
        "tigrbl_rs_ports",
    ]
    assert plan["crate_publish_order"] == ["tigrbl_rs_spec", "tigrbl_rs_ports"]
    assert plan["package_selection"] == [
        "tigrbl_acme_ca",
        "tigrbl_rs_ports",
        "tigrbl_rs_spec",
    ]


def test_unknown_package_selection_fails() -> None:
    with pytest.raises(ValueError, match="unknown package"):
        build_plan("patch", write_changes=False, packages="does-not-exist")


def test_publish_crates_dry_run_uses_cargo_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    summary = tmp_path / "release-plan.json"
    summary.write_text(
        json.dumps(
            {
                "crates": [
                    {"name": "tigrbl_rs_spec", "version": "0.1.10-dev.1"},
                    {"name": "tigrbl_rs_ports", "version": "0.1.10-dev.1"},
                ],
                "crate_publish_order": ["tigrbl_rs_spec", "tigrbl_rs_ports"],
            }
        ),
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(release_automation, "run", lambda args, **kwargs: calls.append(args))

    release_automation.publish_crates(summary, dry_run=True)

    assert calls == [
        ["cargo", "package", "-p", "tigrbl_rs_spec", "--locked"],
        [
            "cargo",
            "package",
            "-p",
            "tigrbl_rs_ports",
            "--locked",
            "--config",
            f'patch.crates-io.tigrbl_rs_spec.path="{release_automation.ROOT.joinpath("target", "package", "tigrbl_rs_spec-0.1.10-dev.1").as_posix()}"',
        ],
    ]


def test_publish_crates_verify_uses_package_before_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "release-plan.json"
    summary.write_text(
        json.dumps(
            {
                "crates": [{"name": "tigrbl_rs_spec", "version": "0.1.10-dev.1"}],
                "crate_publish_order": ["tigrbl_rs_spec"],
            }
        ),
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(release_automation, "run", lambda args, **kwargs: calls.append(args))
    monkeypatch.setattr(release_automation.time, "sleep", lambda seconds: None)

    release_automation.publish_crates(summary, dry_run=False, verify=True)

    assert calls == [
        ["cargo", "package", "-p", "tigrbl_rs_spec", "--locked"],
        ["cargo", "publish", "-p", "tigrbl_rs_spec", "--locked"],
    ]
