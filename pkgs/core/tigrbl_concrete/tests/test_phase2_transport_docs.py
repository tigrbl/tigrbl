from __future__ import annotations

from pathlib import Path

def test_asyncapi_docs_builder_source_is_removed() -> None:
    root = Path(__file__).resolve().parents[4]
    asyncapi_builder = (
        root / "pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/asyncapi.py"
    )

    assert not asyncapi_builder.exists()
