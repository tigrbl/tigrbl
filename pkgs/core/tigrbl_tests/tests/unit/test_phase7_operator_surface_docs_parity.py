from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def test_operator_surface_reference_pages_exist() -> None:
    pages = [
        ROOT / "docs/developer/operator/README.md",
        ROOT / "docs/developer/operator/docs-ui.md",
        ROOT / "docs/developer/operator/static-files.md",
        ROOT / "docs/developer/operator/cookies-and-streaming.md",
        ROOT / "docs/developer/operator/websockets-and-sse.md",
        ROOT / "docs/developer/operator/forms-and-uploads.md",
        ROOT / "docs/developer/operator/middleware-catalog.md",
    ]
    missing = [str(page.relative_to(ROOT)) for page in pages if not page.is_file()]
    assert not missing, f"missing operator reference pages: {missing}"


def test_operator_surface_docs_record_de_scoped_docs_ui_and_auth_decisions() -> None:
    current_target = (ROOT / "docs/conformance/CURRENT_TARGET.md").read_text(encoding="utf-8")
    operator_surfaces = (ROOT / "docs/developer/OPERATOR_SURFACES.md").read_text(encoding="utf-8")
    middleware_catalog = (ROOT / "docs/developer/operator/middleware-catalog.md").read_text(encoding="utf-8")
    docs_ui = (ROOT / "docs/developer/operator/docs-ui.md").read_text(encoding="utf-8")

    assert "AsyncAPI UI" in current_target
    assert "de-scoped" in current_target
    assert "JSON Schema UI" in current_target
    assert "OIDC discovery/docs surface" in current_target
    assert "dependency/hook-based only" in middleware_catalog
    assert "CORSMiddleware" in operator_surfaces
    assert "/asyncapi.json" in docs_ui
    assert "/schemas.json" in docs_ui
