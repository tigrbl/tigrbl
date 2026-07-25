from __future__ import annotations

from typing import Any, get_type_hints

from pydantic import TypeAdapter


JsonSchema = dict[str, Any]
_PYDANTIC_DECIMAL_PATTERN = r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$"
_JSON_DECIMAL_PATTERN = r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*(?:[eE][+-]?\d+)?$"


def _normalize_runtime_schema(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {key: _normalize_runtime_schema(item) for key, item in value.items()}
        if normalized.get("pattern") == _PYDANTIC_DECIMAL_PATTERN:
            normalized["pattern"] = _JSON_DECIMAL_PATTERN
        return normalized
    if isinstance(value, list):
        return [_normalize_runtime_schema(item) for item in value]
    return value


def _model_json_schema(model: Any, *, ref_template: str) -> JsonSchema:
    if model is None:
        return {"type": "object", "properties": {}, "additionalProperties": False}
    exporter = getattr(model, "model_json_schema", None)
    if not callable(exporter):
        raise TypeError(f"Bound schema {model!r} does not expose model_json_schema().")
    return _normalize_runtime_schema(dict(exporter(ref_template=ref_template)))


def build_operation_result_json_schema(
    operation: Any,
    output_model: Any,
    *,
    handler: Any | None = None,
    ref_template: str = "#/$defs/{model}",
) -> JsonSchema:
    """Build the JSON Schema for the complete value returned by an operation."""

    target = str(getattr(operation, "target", ""))
    model_schema = _model_json_schema(output_model, ref_template=ref_template)
    if target == "list" and model_schema.get("type") != "array":
        return _normalize_runtime_schema(
            dict(TypeAdapter(list[output_model]).json_schema(ref_template=ref_template))
        )

    if (
        target == "custom"
        and getattr(operation, "response_model", None) is None
        and callable(handler)
    ):
        try:
            annotation = get_type_hints(handler).get("return")
        except (NameError, TypeError):
            annotation = None
        if annotation is not None:
            return _normalize_runtime_schema(
                dict(TypeAdapter(annotation).json_schema(ref_template=ref_template))
            )

    return model_schema


__all__ = ["build_operation_result_json_schema"]
