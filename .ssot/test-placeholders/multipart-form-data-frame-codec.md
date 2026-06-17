# Multipart/Form-Data Frame Codec Tracking

Planned coverage for a runtime `multipart/form-data` frame codec.

Scope:
- Track `multipart/form-data` as the only additional frame codec family under consideration.
- Keep YAML, CBOR, msgpack, protobuf, Avro, and gRPC frame codecs out of scope.
- Verify any future implementation preserves multipart boundaries, part headers, file parts, form fields, and fail-closed malformed body behavior.
