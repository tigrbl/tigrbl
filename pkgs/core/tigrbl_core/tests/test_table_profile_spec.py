from __future__ import annotations

import pytest

from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.table_profile_spec import (
    PLAIN_TABLE_PROFILE,
    TableProfileError,
    TableProfileSpec,
    make_profile_op,
    register_table_profile,
)
from tigrbl_spec import CURRENT_SCHEMA_VERSION, validate_payload, with_identity


def test_table_profile_spec_round_trips_with_ops() -> None:
    profile = TableProfileSpec(
        kind="acme.audit",
        role="concrete",
        ops=(make_profile_op("read"),),
        default_bindings=(),
        docs_exposure="declared",
        runtime_exposure="none",
        custom=True,
        namespace="acme",
    )

    restored = TableProfileSpec.from_dict(profile.to_dict())

    assert restored == profile
    assert restored.ops[0].target == "read"


def test_table_profile_spec_rejects_non_ops() -> None:
    with pytest.raises(TableProfileError, match="ops entries must be OpSpec"):
        TableProfileSpec(kind="bad", ops=("read",))  # type: ignore[arg-type]


def test_custom_table_profile_requires_namespace() -> None:
    with pytest.raises(TableProfileError, match="require a namespace"):
        TableProfileSpec(kind="acme.audit", custom=True)


def test_custom_table_profile_cannot_use_reserved_builtin_name() -> None:
    with pytest.raises(TableProfileError, match="reserved kind"):
        TableProfileSpec(kind="rest", custom=True, namespace="acme")


def test_table_profile_schema_validates_serialized_payload() -> None:
    payload = with_identity("TableProfileSpec", PLAIN_TABLE_PROFILE.to_dict())

    validated = validate_payload("TableProfileSpec", payload)

    assert validated["spec_schema_version"] == CURRENT_SCHEMA_VERSION
    assert validated["kind"] == "plain"


def test_table_profile_schema_rejects_invalid_role() -> None:
    payload = with_identity(
        "TableProfileSpec",
        {
            "kind": "plain",
            "role": "maybe",
            "ops": {"__tuple__": []},
            "default_bindings": {"__tuple__": []},
            "docs_exposure": "none",
            "runtime_exposure": "none",
            "custom": False,
            "namespace": None,
        },
    )

    with pytest.raises(Exception, match="TableProfileSpec payload"):
        validate_payload("TableProfileSpec", payload)


def test_table_profile_registry_rejects_duplicate_builtin() -> None:
    with pytest.raises(TableProfileError, match="already registered"):
        register_table_profile(PLAIN_TABLE_PROFILE)


def test_registered_custom_table_profile_is_returned() -> None:
    profile = TableProfileSpec(
        kind="testpkg.single_read",
        role="concrete",
        ops=(OpSpec(alias="read", target="read"),),
        custom=True,
        namespace="testpkg",
    )

    registered = register_table_profile(profile)

    assert registered.kind == "testpkg.single_read"
