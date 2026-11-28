from __future__ import annotations

import importlib

import pytest

from tigrbl_spec import validate_payload
from .helpers import representative_payloads


@pytest.mark.parametrize("spec_kind", sorted(representative_payloads()))
def test_generated_dataclass_compatibility_corpus(spec_kind: str) -> None:
    models = importlib.import_module("tigrbl_spec.models.v0_3_20")
    model_cls = getattr(models, spec_kind)
    payload = representative_payloads()[spec_kind]

    model = model_cls.from_dict(payload)
    serialized = model.to_dict()

    assert serialized == payload
    assert validate_payload(spec_kind, serialized) == payload
