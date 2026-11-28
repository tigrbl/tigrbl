from __future__ import annotations

from tigrbl_spec import validate_payload
from tigrbl_spec.models.v0_3_20 import AppSpec
from .helpers import app_payload


def test_generated_dataclass_roundtrips_and_revalidates() -> None:
    payload = app_payload()

    model = AppSpec.from_dict(payload)
    serialized = model.to_dict()

    assert serialized == payload
    assert validate_payload("AppSpec", serialized) == payload
