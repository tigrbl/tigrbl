from __future__ import annotations

from tigrbl_core._spec.schema_spec import SchemaArg, SchemaRef
from .get_schema import get_schema
from .builder.build_schema import _build_schema
from .builder.list_params import _build_list_params
from .spec_json import (
    INDIVIDUAL_SPEC_NAMES,
    JSON_SCHEMA_DRAFT_2020_12,
    SHARED_SCHEMA_NAME,
    build_individual_spec_json_schemas,
    build_shared_json_schema,
    build_spec_json_schema_bundle,
)
from .utils import (
    namely_model,
    _make_bulk_ids_model,
    _make_bulk_rows_model,
    _make_bulk_rows_response_model,
    _make_deleted_response_model,
    _make_pk_model,
)

__all__ = [
    "get_schema",
    "SchemaRef",
    "SchemaArg",
    "_build_schema",
    "_build_list_params",
    "_make_bulk_rows_model",
    "_make_bulk_rows_response_model",
    "_make_bulk_ids_model",
    "_make_deleted_response_model",
    "_make_pk_model",
    "namely_model",
    "INDIVIDUAL_SPEC_NAMES",
    "JSON_SCHEMA_DRAFT_2020_12",
    "SHARED_SCHEMA_NAME",
    "build_individual_spec_json_schemas",
    "build_shared_json_schema",
    "build_spec_json_schema_bundle",
]
