from __future__ import annotations

import hashlib
import json
import zlib
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

RESULTS_PATH = Path(__file__).with_name("compiled_input_strategy_microbench.json")
HASH_ITERATIONS = 250_000
DECODE_ITERATIONS = 200_000
SAMPLE_COUNT = 5


def _hash_blake2b64(value: str, *, lowercase: bool = False) -> int:
    normalized = value.lower() if lowercase else value
    digest = hashlib.blake2b(normalized.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def _hash_zlib64(value: str, *, lowercase: bool = False) -> int:
    normalized = value.lower() if lowercase else value
    encoded = normalized.encode("utf-8")
    lo = zlib.crc32(encoded) & 0xFFFFFFFF
    hi = zlib.crc32(encoded, 0x9E3779B9) & 0xFFFFFFFF
    return (hi << 32) | lo


def _build_hashed_items(
    payload: dict[str, Any],
    hash_fn: Callable[[str], int],
) -> dict[int, Any]:
    return {hash_fn(key): value for key, value in payload.items()}


def _decode_generic_hashed(
    payload: dict[str, Any],
    lookup_hashes: tuple[int, ...],
    field_names: tuple[str, ...],
    hash_fn: Callable[[str], int],
) -> dict[str, Any]:
    hashed_items = _build_hashed_items(payload, hash_fn)
    out: dict[str, Any] = {}
    for field_name, lookup_hash in zip(field_names, lookup_hashes):
        value = hashed_items.get(lookup_hash)
        if value is not None:
            out[field_name] = value
    return out


def _decode_specialized_mapping(
    payload: dict[str, Any],
    lookup_names: tuple[str, ...],
    field_names: tuple[str, ...],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for field_name, lookup_name in zip(field_names, lookup_names):
        value = payload.get(lookup_name)
        if value is not None:
            out[field_name] = value
    return out


def _decode_specialized_single_field(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("name")
    if value is None:
        return {}
    return {"name": value}


def _benchmark(
    *,
    title: str,
    iterations: int,
    samples: int,
    func: Callable[[], Any],
) -> dict[str, Any]:
    sample_times: list[float] = []
    func()
    for _ in range(samples):
        start = perf_counter()
        for _ in range(iterations):
            func()
        elapsed = perf_counter() - start
        sample_times.append(elapsed)
    mean_seconds = mean(sample_times)
    return {
        "title": title,
        "iterations": iterations,
        "samples": samples,
        "mean_seconds": mean_seconds,
        "ops_per_second": iterations / mean_seconds if mean_seconds else 0.0,
        "mean_ns_per_op": (mean_seconds / iterations) * 1_000_000_000
        if iterations
        else 0.0,
        "sample_seconds": sample_times,
    }


def _profile_hashes() -> list[dict[str, Any]]:
    sample = "BenchmarkItem.create"
    return [
        _benchmark(
            title="hash.blake2b64",
            iterations=HASH_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _hash_blake2b64(sample),
        ),
        _benchmark(
            title="hash.zlib_crc32x2_64",
            iterations=HASH_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _hash_zlib64(sample),
        ),
    ]


def _profile_body_only_shapes() -> list[dict[str, Any]]:
    one_field_payload = {"name": "Ada"}
    one_field_names = ("name",)
    one_field_lookup_names = ("name",)
    one_field_lookup_hashes_blake2b = tuple(
        _hash_blake2b64(name) for name in one_field_lookup_names
    )
    one_field_lookup_hashes_zlib = tuple(
        _hash_zlib64(name) for name in one_field_lookup_names
    )

    four_field_payload = {
        "name": "Ada",
        "role": "operator",
        "region": "us-central",
        "tenant": "acme",
    }
    four_field_names = ("name", "role", "region", "tenant")
    four_field_lookup_names = four_field_names
    four_field_lookup_hashes_blake2b = tuple(
        _hash_blake2b64(name) for name in four_field_lookup_names
    )
    four_field_lookup_hashes_zlib = tuple(
        _hash_zlib64(name) for name in four_field_lookup_names
    )

    return [
        _benchmark(
            title="shape.body_only_1.generic_hashed_blake2b",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_generic_hashed(
                one_field_payload,
                one_field_lookup_hashes_blake2b,
                one_field_names,
                _hash_blake2b64,
            ),
        ),
        _benchmark(
            title="shape.body_only_1.generic_hashed_zlib",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_generic_hashed(
                one_field_payload,
                one_field_lookup_hashes_zlib,
                one_field_names,
                _hash_zlib64,
            ),
        ),
        _benchmark(
            title="shape.body_only_1.specialized_mapping",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_specialized_mapping(
                one_field_payload, one_field_lookup_names, one_field_names
            ),
        ),
        _benchmark(
            title="shape.body_only_1.specialized_single_field",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_specialized_single_field(one_field_payload),
        ),
        _benchmark(
            title="shape.body_only_4.generic_hashed_blake2b",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_generic_hashed(
                four_field_payload,
                four_field_lookup_hashes_blake2b,
                four_field_names,
                _hash_blake2b64,
            ),
        ),
        _benchmark(
            title="shape.body_only_4.generic_hashed_zlib",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_generic_hashed(
                four_field_payload,
                four_field_lookup_hashes_zlib,
                four_field_names,
                _hash_zlib64,
            ),
        ),
        _benchmark(
            title="shape.body_only_4.specialized_mapping",
            iterations=DECODE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _decode_specialized_mapping(
                four_field_payload, four_field_lookup_names, four_field_names
            ),
        ),
    ]


@pytest.mark.perf
def test_compiled_input_strategy_microbench() -> None:
    hash_results = _profile_hashes()
    shape_results = _profile_body_only_shapes()

    payload = {
        "hash_iterations": HASH_ITERATIONS,
        "decode_iterations": DECODE_ITERATIONS,
        "samples": SAMPLE_COUNT,
        "hash_results": hash_results,
        "shape_results": shape_results,
        "artifact_path": str(RESULTS_PATH),
    }

    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert RESULTS_PATH.exists()
    assert all(result["ops_per_second"] > 0 for result in hash_results)
    assert all(result["ops_per_second"] > 0 for result in shape_results)

    hash_ops = {result["title"]: result["ops_per_second"] for result in hash_results}
    shape_ops = {result["title"]: result["ops_per_second"] for result in shape_results}

    assert hash_ops["hash.zlib_crc32x2_64"] > hash_ops["hash.blake2b64"]
    assert (
        shape_ops["shape.body_only_1.specialized_single_field"]
        > shape_ops["shape.body_only_1.specialized_mapping"]
        > shape_ops["shape.body_only_1.generic_hashed_zlib"]
        > shape_ops["shape.body_only_1.generic_hashed_blake2b"]
    )
    assert (
        shape_ops["shape.body_only_4.specialized_mapping"]
        > shape_ops["shape.body_only_4.generic_hashed_zlib"]
        > shape_ops["shape.body_only_4.generic_hashed_blake2b"]
    )
