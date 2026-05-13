"""Crop README banner strips from the generated TIGRBL banner sheet.

The script detects strong horizontal cyan divider lines and writes each region
between dividers as a standalone PNG. It intentionally uses only the Python
standard library so it can run in the repo without a Pillow dependency.
"""

from __future__ import annotations

import argparse
import binascii
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class PngImage:
    width: int
    height: int
    color_type: int
    bit_depth: int
    pixels: list[bytes]

    @property
    def channels(self) -> int:
        if self.color_type == 2:
            return 3
        if self.color_type == 6:
            return 4
        raise ValueError(f"unsupported PNG color type: {self.color_type}")

    @property
    def row_bytes(self) -> int:
        return self.width * self.channels


def _iter_chunks(data: bytes):
    pos = len(PNG_SIGNATURE)
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated PNG chunk header")
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        start = pos + 8
        end = start + length
        crc_end = end + 4
        if crc_end > len(data):
            raise ValueError(f"truncated PNG chunk {kind!r}")
        yield kind, data[start:end]
        pos = crc_end
        if kind == b"IEND":
            break


def read_png(path: Path) -> PngImage:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{path} is not a PNG")

    width = height = color_type = bit_depth = None
    interlace = None
    compressed = bytearray()

    for kind, payload in _iter_chunks(data):
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _comp, _filter, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break

    if width is None or height is None or color_type is None or bit_depth is None:
        raise ValueError("missing IHDR")
    if bit_depth != 8:
        raise ValueError(f"unsupported bit depth {bit_depth}; expected 8")
    if color_type not in (2, 6):
        raise ValueError(f"unsupported color type {color_type}; expected RGB or RGBA")
    if interlace != 0:
        raise ValueError("interlaced PNGs are not supported")

    channels = 4 if color_type == 6 else 3
    row_bytes = width * channels
    raw = zlib.decompress(bytes(compressed))
    expected = height * (row_bytes + 1)
    if len(raw) != expected:
        raise ValueError(f"unexpected decompressed size {len(raw)}; expected {expected}")

    rows: list[bytes] = []
    prev = bytes(row_bytes)
    stride = row_bytes + 1
    for y in range(height):
        filter_type = raw[y * stride]
        scanline = bytearray(raw[y * stride + 1 : (y + 1) * stride])
        recon = _unfilter_scanline(filter_type, scanline, prev, channels)
        rows.append(bytes(recon))
        prev = bytes(recon)

    return PngImage(width, height, color_type, bit_depth, rows)


def _unfilter_scanline(
    filter_type: int, scanline: bytearray, prev: bytes, bytes_per_pixel: int
) -> bytearray:
    out = bytearray(scanline)
    for i, value in enumerate(scanline):
        left = out[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
        up = prev[i]
        up_left = prev[i - bytes_per_pixel] if i >= bytes_per_pixel else 0

        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        elif filter_type == 4:
            predictor = _paeth(left, up, up_left)
        else:
            raise ValueError(f"unsupported PNG filter type {filter_type}")

        out[i] = (value + predictor) & 0xFF
    return out


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def write_png(path: Path, image: PngImage, y0: int, y1: int) -> None:
    height = y1 - y0
    if height <= 0:
        raise ValueError(f"invalid crop range {y0}:{y1}")

    raw = bytearray()
    for row in image.pixels[y0:y1]:
        raw.append(0)
        raw.extend(row)

    ihdr = struct.pack(
        ">IIBBBBB",
        image.width,
        height,
        image.bit_depth,
        image.color_type,
        0,
        0,
        0,
    )
    payload = PNG_SIGNATURE
    payload += _chunk(b"IHDR", ihdr)
    payload += _chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
    payload += _chunk(b"IEND", b"")
    path.write_bytes(payload)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind)
    crc = binascii.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def cyan_score(row: bytes, channels: int) -> float:
    hits = 0
    pixels = len(row) // channels
    for i in range(0, len(row), channels):
        r, g, b = row[i], row[i + 1], row[i + 2]
        if g >= 120 and b >= 135 and r <= 70 and (g + b) >= 290:
            hits += 1
    return hits / pixels


def detect_dividers(
    image: PngImage,
    min_row_score: float,
    _min_gap: int,
) -> list[int]:
    candidates = [
        y
        for y, row in enumerate(image.pixels)
        if cyan_score(row, image.channels) >= min_row_score
    ]
    if not candidates:
        return []

    clusters: list[list[int]] = []
    current = [candidates[0]]
    for y in candidates[1:]:
        if y == current[-1] + 1:
            current.append(y)
        else:
            clusters.append(current)
            current = [y]
    clusters.append(current)

    return [
        (cluster[0] + cluster[-1]) // 2
        for cluster in clusters
    ]


def select_section_boundaries(
    height: int,
    candidates: list[int],
    expected_sections: int,
) -> list[int]:
    """Choose the boundary set that yields the most even expected sections.

    Generated sheets can contain other strong cyan horizontal lines inside a
    banner. This keeps divider detection line-based but rejects internal rails.
    """

    if expected_sections <= 0:
        raise ValueError("expected_sections must be positive")

    normalized = sorted(set(candidates))
    if not normalized or normalized[0] > 6:
        normalized.insert(0, 0)
    else:
        normalized[0] = 0
    if normalized[-1] < height - 7:
        normalized.append(height)
    else:
        normalized[-1] = height

    target = height / expected_sections
    boundary_count = expected_sections + 1
    if len(normalized) <= boundary_count:
        return normalized

    interior = normalized[1:-1]
    needed = expected_sections - 1
    best: tuple[float, list[int]] | None = None

    def walk(start: int, chosen: list[int]) -> None:
        nonlocal best
        if len(chosen) == needed:
            boundaries = [0, *chosen, height]
            segment_heights = [
                end - begin for begin, end in zip(boundaries, boundaries[1:])
            ]
            score = sum((segment - target) ** 2 for segment in segment_heights)
            if best is None or score < best[0]:
                best = (score, boundaries)
            return

        remaining = needed - len(chosen)
        for i in range(start, len(interior) - remaining + 1):
            walk(i + 1, [*chosen, interior[i]])

    walk(0, [])
    if best is None:
        return normalized
    return best[1]


def crop_ranges(height: int, dividers: list[int], padding: int) -> list[tuple[int, int]]:
    edges = dividers
    ranges: list[tuple[int, int]] = []
    for start, end in zip(edges, edges[1:]):
        y0 = min(max(start + padding, 0), height)
        y1 = min(max(end - padding, 0), height)
        if y1 - y0 > 20:
            ranges.append((y0, y1))
    return ranges


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split a TIGRBL README banner sheet into separate PNG banners."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="docs/assets/tigrbl-readme-banner-sheet-raw.png",
        help="Path to the raw banner sheet PNG.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/assets/readme-banners",
        help="Directory where cropped banners are written.",
    )
    parser.add_argument(
        "--prefix",
        default="tigrbl-readme-banner",
        help="Filename prefix for generated crops.",
    )
    parser.add_argument(
        "--min-row-score",
        type=float,
        default=0.35,
        help="Minimum fraction of cyan pixels needed to treat a row as a divider.",
    )
    parser.add_argument(
        "--divider-padding",
        type=int,
        default=14,
        help="Pixels to trim on each side of detected divider lines.",
    )
    parser.add_argument(
        "--expected",
        type=int,
        default=6,
        help="Expected number of output banners. Used for validation only.",
    )
    parser.add_argument(
        "--fallback-equal-split",
        action="store_true",
        help="Split into expected equal rows if divider detection fails.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.out_dir)
    image = read_png(input_path)
    min_gap = max(12, image.height // max(args.expected * 2, 1))
    dividers = detect_dividers(image, args.min_row_score, min_gap)
    boundaries = select_section_boundaries(image.height, dividers, args.expected)
    ranges = crop_ranges(image.height, boundaries, args.divider_padding)

    if len(ranges) != args.expected and args.fallback_equal_split:
        step = image.height // args.expected
        ranges = [
            (i * step, image.height if i == args.expected - 1 else (i + 1) * step)
            for i in range(args.expected)
        ]

    if len(ranges) != args.expected:
        raise SystemExit(
            f"detected {len(ranges)} banners from {len(dividers)} divider candidates; "
            f"expected {args.expected}. Try --min-row-score or --fallback-equal-split."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    for index, (y0, y1) in enumerate(ranges, start=1):
        out_path = output_dir / f"{args.prefix}-{index:02d}.png"
        write_png(out_path, image, y0, y1)
        print(f"{out_path} y={y0}:{y1} size={image.width}x{y1-y0}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
