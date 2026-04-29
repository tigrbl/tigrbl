from __future__ import annotations


def compile_static_file_chain(
    *,
    range_requests: bool = False,
    cache_headers: bool = False,
    pathsend: bool = False,
) -> dict[str, object]:
    atoms = [
        "transport.ingress",
        "static_file.route.resolve",
        "static_file.path.validate",
        "static_file.lookup",
    ]
    if range_requests:
        atoms.append("static_file.range.parse")
    if cache_headers:
        atoms.append("static_file.cache.headers")
    atoms.append("transport.pathsend" if pathsend else "transport.emit")
    atoms.append("transport.emit_complete")
    return {
        "binding": "static.file",
        "family": "static_file",
        "atoms": tuple(atoms),
        "completion_fence": "POST_EMIT",
    }


__all__ = ["compile_static_file_chain"]
