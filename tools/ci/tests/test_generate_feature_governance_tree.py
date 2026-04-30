from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from generate_feature_governance_tree import build_report, render_markdown  # noqa: E402


def test_governance_tree_builds_direct_adr_spec_feature_hierarchy(tmp_path: Path) -> None:
    (tmp_path / ".ssot" / "adr").mkdir(parents=True)
    (tmp_path / ".ssot" / "specs").mkdir(parents=True)
    (tmp_path / ".ssot" / "adr" / "ADR-1003-test.yaml").write_text("title: adr\n", encoding="utf-8")
    (tmp_path / ".ssot" / "specs" / "SPEC-1000-test.yaml").write_text("title: spec\n", encoding="utf-8")
    (tmp_path / ".ssot" / "specs" / "SPEC-3000-test.yaml").write_text("title: orphan\n", encoding="utf-8")

    registry = {
        "features": [
            {
                "id": "feat:a",
                "title": "Feature A",
                "implementation_status": "implemented",
                "adr_ids": [],
                "spec_ids": ["spc:1000"],
            },
            {
                "id": "feat:b",
                "title": "Feature B",
                "implementation_status": "partial",
                "adr_ids": [],
                "spec_ids": ["spc:3000"],
            },
        ],
        "adrs": [
            {
                "id": "adr:1003",
                "title": "ADR Root",
                "path": ".ssot/adr/ADR-1003-test.yaml",
            }
        ],
        "specs": [
            {
                "id": "spc:1000",
                "title": "Spec Child",
                "path": ".ssot/specs/SPEC-1000-test.yaml",
                "adr_ids": ["adr:1003"],
            },
            {
                "id": "spc:3000",
                "title": "Orphan Spec",
                "path": ".ssot/specs/SPEC-3000-test.yaml",
                "adr_ids": [],
            },
        ],
    }

    report = build_report(
        registry,
        selected_feature_ids=["feat:b", "feat:a"],
        highlighted_adr_ids=["adr:1003"],
        highlighted_spec_ids=["spc:1000"],
        root=tmp_path,
    )

    assert report["adrs"][0]["adr_id"] == "adr:1003"
    assert [spec["spec_id"] for spec in report["adrs"][0]["specs"]] == ["spc:1000"]
    assert [feature["feature_id"] for feature in report["features_by_spec"]["spc:1000"]] == ["feat:a"]
    assert [spec["spec_id"] for spec in report["orphan_specs"]] == ["spc:3000"]
    assert [feature["feature_id"] for feature in report["features_by_spec"]["spc:3000"]] == ["feat:b"]
    assert report["feature_orphans"] == []

    markdown = render_markdown(report)
    assert "- `adr:1003` ADR Root" in markdown
    assert "  - `spc:1000` Spec Child" in markdown
    assert "    - `feat:a` Feature A (`implemented`)" in markdown
    assert "- `spc:3000` Orphan Spec" in markdown
