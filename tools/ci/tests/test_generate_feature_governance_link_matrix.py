from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from generate_feature_governance_link_matrix import build_report, render_markdown  # noqa: E402


def test_feature_governance_matrix_keeps_highlighted_columns_and_direct_links_only(tmp_path: Path) -> None:
    (tmp_path / ".ssot" / "adr").mkdir(parents=True)
    (tmp_path / ".ssot" / "specs").mkdir(parents=True)
    (tmp_path / ".ssot" / "adr" / "ADR-1003-test.yaml").write_text("title: test\n", encoding="utf-8")
    (tmp_path / ".ssot" / "specs" / "SPEC-1000-test.yaml").write_text("title: test\n", encoding="utf-8")
    (tmp_path / ".ssot" / "specs" / "SPEC-3000-test.yaml").write_text("title: test\n", encoding="utf-8")

    registry = {
        "features": [
            {
                "id": "feat:a",
                "title": "Feature A",
                "implementation_status": "implemented",
                "adr_ids": [],
                "spec_ids": ["spc:3000"],
            },
            {
                "id": "feat:b",
                "title": "Feature B",
                "implementation_status": "partial",
                "adr_ids": [],
                "spec_ids": [],
            },
        ],
        "adrs": [
            {
                "id": "adr:1003",
                "title": "Spec First",
                "path": ".ssot/adr/ADR-1003-test.yaml",
            }
        ],
        "specs": [
            {
                "id": "spc:1000",
                "title": "AppSpec",
                "path": ".ssot/specs/SPEC-1000-test.yaml",
            },
            {
                "id": "spc:3000",
                "title": "Additional Spec",
                "path": ".ssot/specs/SPEC-3000-test.yaml",
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

    assert [row["feature_id"] for row in report["rows"]] == ["feat:a", "feat:b"]
    assert report["column_adr_ids"] == ["adr:1003"]
    assert report["column_spec_ids"] == ["spc:1000", "spc:3000"]
    assert report["additional_spec_ids"] == ["spc:3000"]
    assert report["rows"][0]["spec_ids"] == ["spc:3000"]
    assert report["rows"][1]["spec_ids"] == []

    markdown_one = render_markdown(report)
    markdown_two = render_markdown(report)
    assert markdown_one == markdown_two
    assert "| `feat:a` | Feature A | `implemented` |" in markdown_one
    assert "| `spc:3000` | Additional Spec |" in markdown_one

