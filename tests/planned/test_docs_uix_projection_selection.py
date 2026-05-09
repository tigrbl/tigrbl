from tigrbl_core._spec import DocsUixSpec

from ._nested_appspec_support import multisurface_paths


def test_docs_uix_path_points_to_payload_without_owning_projection_rules() -> None:
    docs_path = next(path for path in multisurface_paths() if path.path == "/docs")

    assert docs_path.kind == "docs-uix"
    assert isinstance(docs_path.docs_uix, DocsUixSpec)
    assert docs_path.docs_uix.kind == "swagger"
    assert docs_path.docs_uix.payload_path == "/openapi.json"
    assert docs_path.docs_uix.projection is None
