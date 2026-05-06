from __future__ import annotations

from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core.config.resolver import resolve_cfg


def test_batch_config_defaults_are_disabled_and_sized() -> None:
    batch = resolve_cfg().batch

    assert batch["enabled"] is False
    assert batch["max_size"] == 64
    assert batch["max_bytes"] == 1_048_576
    assert batch["max_delay_ms"] == 1


def test_opspec_batch_config_overrides_defaults() -> None:
    cfg = resolve_cfg(
        op="create",
        opspec=OpSpec(
            alias="create",
            target="create",
            batch={"enabled": True, "max_size": 8},
        ),
    )

    assert cfg.batch["enabled"] is True
    assert cfg.batch["max_size"] == 8
    assert cfg.batch["max_bytes"] == 1_048_576
