"""Versioned event envelope shared by the exporter and collector."""

from collections.abc import Mapping
from math import isfinite
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from tigrbl_typing.trace import TRACE_EXECUTION_FIELDS, TRACE_ID_FIELDS

WIRE_VERSION = 1
BATCH_SIZE = 50
MAX_BODY_BYTES = 3 * 1024 * 1024
SourceName = Annotated[str, Field(pattern=r"^[a-zA-Z0-9_.-]{1,100}$")]


def select_fields(fields: Mapping) -> dict:
    result = {}
    for key in (
        *TRACE_ID_FIELDS,
        "rpc_item_index",
        "trace_id",
        "span_id",
        "parent_span_id",
        "status",
        "outcome",
        *TRACE_EXECUTION_FIELDS,
        "measured_duration_ms",
        "atom_ordinal",
        "atom_trace_dropped",
    ):
        value = fields.get(key)
        if isinstance(value, str):
            encoded = value[:256].replace("\x00", "").encode("utf-8", errors="replace")
            result[key] = encoded[:256].decode("utf-8", errors="ignore")
        elif (
            type(value) is int
            and -(2**63) <= value < 2**63
            or type(value) is float
            and isfinite(value)
        ):
            result[key] = value
    if fields.get("path") == "/rpc":
        result["path"] = "/rpc"
    return result


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sequence: Annotated[int, Field(strict=True, gt=0, lt=2**63)]
    captured_at: AwareDatetime
    kind: Annotated[str, Field(pattern=r"^[ -~]{1,100}$")]
    transport: Annotated[str, Field(pattern=r"^[ -~]{1,32}$")]
    fields: dict

    @field_validator("fields")
    @classmethod
    def identity_fields_only(cls, value):
        return select_fields(value)


class BatchSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service: SourceName
    environment: SourceName
    worker_boot_id: Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]


class Batch(BatchSource):
    version: Literal[1]
    events: Annotated[list[Event], Field(min_length=1, max_length=BATCH_SIZE)]
