#!/usr/bin/env python3
"""
Triage Test Runner for tigrbl_tests.

Runs pytest with --json-report, then categorizes failures into concern
buckets grouped by error signature. Helps identify root causes quickly.

Usage:
    python triage_tests.py                  # run all tests
    python triage_tests.py -x               # stop on first failure
    python triage_tests.py -m unit          # only unit tests
    python triage_tests.py --no-color       # plain output for CI
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ── Concern Definitions ────────────────────────────────────────────────

CONCERNS = [
    (
        "COLLECTION",
        "COLLECTION ERRORS",
        "These tests could not even be imported/collected. Fix these first.",
    ),
    (
        "UNIT",
        "UNIT TEST FAILURES",
        "Core logic is broken. These indicate bugs in tigrbl internals.",
    ),
    (
        "INTEGRATION",
        "INTEGRATION TEST FAILURES",
        "End-to-end flows are broken (HTTP, DB, uvicorn).",
    ),
    (
        "HARNESS",
        "ARCHITECTURE / HARNESS FAILURES",
        "Design constraints or compilation contracts violated.",
    ),
    ("OTHER", "ACCEPTANCE / PERF / OTHER", "Non-critical. Address after collection, unit, integration, and harness failures."),
    (
        "XFAIL",
        "EXPECTED FAILURES",
        "xfail tests that unexpectedly passed (investigate marker removal).",
    ),
]

# ── ANSI Colors ─────────────────────────────────────────────────────────

_COLOR = {
    "COLLECTION": "\033[1;31m",  # bold red
    "UNIT": "\033[0;31m",  # red
    "INTEGRATION": "\033[0;33m",  # yellow
    "HARNESS": "\033[0;36m",  # cyan
    "OTHER": "\033[0;37m",  # white
    "XFAIL": "\033[2m",  # dim
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "green": "\033[0;32m",
    "red": "\033[0;31m",
}

_NO_COLOR = {k: "" for k in _COLOR}


def _colors(use_color: bool) -> dict[str, str]:
    return _COLOR if use_color else _NO_COLOR


# ── Data Structures ─────────────────────────────────────────────────────


@dataclass
class FailureRecord:
    nodeid: str
    error_type: str
    error_message: str
    longrepr: str


@dataclass
class ErrorGroup:
    signature: str
    display_message: str
    tests: list[str] = field(default_factory=list)


# ── Classification ──────────────────────────────────────────────────────

# Path-based classification patterns
_PATH_RULES: list[tuple[str, re.Pattern]] = [
    ("UNIT", re.compile(r"tests/unit/")),
    ("INTEGRATION", re.compile(r"tests/i9n/")),
    ("HARNESS", re.compile(r"tests/(architecture|harness|harness_e2e|harness_v3|parity)/")),
    ("OTHER", re.compile(r"tests/(perf|acceptance)/")),
]

# Marker-based fallback
_MARKER_MAP = {
    "unit": "UNIT",
    "i9n": "INTEGRATION",
    "acceptance": "OTHER",
    "perf": "OTHER",
}


def _classify_test(nodeid: str, markers: list[str], outcome: str) -> str:
    """Return concern bucket for a test."""
    # Collection errors always block all other failure analysis.
    if outcome == "error":
        return "COLLECTION"

    # xfail that unexpectedly passed
    if outcome == "xpassed":
        return "XFAIL"

    # Path-based (most reliable)
    for concern, pattern in _PATH_RULES:
        if pattern.search(nodeid):
            return concern

    # Marker-based fallback
    for marker in markers:
        if marker in _MARKER_MAP:
            return _MARKER_MAP[marker]

    return "OTHER"


# ── Error Signature Extraction ──────────────────────────────────────────

# Patterns to normalize away variable parts
_NORMALIZE_PATTERNS = [
    (re.compile(r"0x[0-9a-fA-F]+"), "0x..."),  # memory addresses
    (re.compile(r"\b[0-9a-f]{8,}\b"), "<id>"),  # hex IDs
    (re.compile(r"'/.+?'"), "'<path>'"),  # file paths
    (re.compile(r"\b\d{4,}\b"), "<num>"),  # large numbers
    (re.compile(r"\bport \d+\b"), "port <N>"),  # port numbers
]


def _extract_error_type(longrepr: str) -> str:
    """Extract the exception class name from the traceback."""
    # Match lines like "E   ImportError: ..." or "ModuleNotFoundError: ..."
    match = re.search(r"(\w*(?:Error|Exception|Warning|Failure))\s*:", longrepr)
    if match:
        return match.group(1)
    # Fallback: look for "ERRORS" or "raised" patterns
    match = re.search(r"raised\s+(\w+)", longrepr)
    if match:
        return match.group(1)
    return "UnknownError"


def _extract_error_message(longrepr: str, error_type: str) -> str:
    """Extract the first line of the error message."""
    pattern = re.compile(re.escape(error_type) + r"\s*:\s*(.+?)(?:\n|$)")
    match = pattern.search(longrepr)
    if match:
        msg = match.group(1).strip()
        # Truncate long messages
        if len(msg) > 120:
            msg = msg[:117] + "..."
        return msg
    return ""


def _normalize_message(msg: str) -> str:
    """Strip variable parts from an error message to create a grouping key."""
    result = msg
    for pattern, replacement in _NORMALIZE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def _make_signature(error_type: str, error_message: str) -> str:
    """Create a groupable signature from error type + normalized message."""
    normalized = _normalize_message(error_message)
    return f"{error_type}: {normalized}"


# ── JSON Report Parsing ─────────────────────────────────────────────────


def _get_markers(test_entry: dict) -> list[str]:
    """Extract marker names from a test entry."""
    markers = []
    for marker in test_entry.get("keywords", []):
        if isinstance(marker, str):
            markers.append(marker)
    return markers


def _parse_longrepr(test_entry: dict) -> str:
    """Get the string representation of the failure."""
    # call phase has the actual test failure
    for phase in ("call", "setup", "teardown", "collect"):
        phase_data = test_entry.get(phase, {})
        if isinstance(phase_data, dict):
            longrepr = phase_data.get("longrepr", "")
            if longrepr:
                return longrepr
    return ""


def parse_report(report: dict) -> dict[str, list[ErrorGroup]]:
    """Parse JSON report into concern buckets of error groups."""
    buckets: dict[str, list[FailureRecord]] = defaultdict(list)

    tests = report.get("tests", [])
    # Also include collectors that errored
    collectors = report.get("collectors", [])

    # Process test results
    for t in tests:
        outcome = t.get("outcome", "")
        nodeid = t.get("nodeid", "")

        if outcome in ("passed", "skipped"):
            continue

        # xpassed = xfail that unexpectedly passed
        if outcome == "xpassed":
            markers = _get_markers(t)
            concern = _classify_test(nodeid, markers, outcome)
            buckets[concern].append(
                FailureRecord(
                    nodeid=nodeid,
                    error_type="UnexpectedPass",
                    error_message="xfail test unexpectedly passed",
                    longrepr="",
                )
            )
            continue

        if outcome not in ("failed", "error"):
            continue

        markers = _get_markers(t)
        longrepr = _parse_longrepr(t)
        error_type = _extract_error_type(longrepr)
        error_message = _extract_error_message(longrepr, error_type)
        concern = _classify_test(nodeid, markers, outcome)

        buckets[concern].append(
            FailureRecord(
                nodeid=nodeid,
                error_type=error_type,
                error_message=error_message,
                longrepr=longrepr,
            )
        )

    # Process collection errors
    for c in collectors:
        outcome = c.get("outcome", "")
        if outcome != "error":
            continue
        nodeid = c.get("nodeid", "")
        longrepr = c.get("longrepr", "")
        error_type = _extract_error_type(longrepr)
        error_message = _extract_error_message(longrepr, error_type)

        buckets["COLLECTION"].append(
            FailureRecord(
                nodeid=nodeid,
                error_type=error_type,
                error_message=error_message,
                longrepr=longrepr,
            )
        )

    # Group failures by error signature within each bucket
    grouped: dict[str, list[ErrorGroup]] = {}
    for concern in ("COLLECTION", "UNIT", "INTEGRATION", "HARNESS", "OTHER", "XFAIL"):
        sig_map: dict[str, ErrorGroup] = {}
        for rec in buckets.get(concern, []):
            sig = _make_signature(rec.error_type, rec.error_message)
            if sig not in sig_map:
                display = (
                    f"{rec.error_type}: {rec.error_message}"
                    if rec.error_message
                    else rec.error_type
                )
                sig_map[sig] = ErrorGroup(signature=sig, display_message=display)
            sig_map[sig].tests.append(rec.nodeid)
        # Sort groups by number of tests (largest first)
        grouped[concern] = sorted(
            sig_map.values(), key=lambda g: len(g.tests), reverse=True
        )

    return grouped


# ── Report Rendering ────────────────────────────────────────────────────

MAX_TESTS_PER_GROUP = 5  # show at most N test names, then "... and M more"
BOX_WIDTH = 62


def _box_line(text: str, width: int = BOX_WIDTH) -> str:
    """Pad text inside a box."""
    return f"  \u2502 {text:<{width - 4}} \u2502"


def render_report(
    grouped: dict[str, list[ErrorGroup]],
    summary: dict,
    c: dict[str, str],
    *,
    max_tests: int = MAX_TESTS_PER_GROUP,
    box_width: int = BOX_WIDTH,
) -> str:
    """Render the full triage report as a string."""
    lines: list[str] = []
    W = box_width

    def _box_line(text: str) -> str:
        return f"  \u2502 {text:<{W - 4}} \u2502"

    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    errors = summary.get("error", 0)
    duration = summary.get("duration", 0.0)

    # Header
    lines.append(f"{c['bold']}{'=' * W}{c['reset']}")
    lines.append(f"{c['bold']}  TIGRBL TEST TRIAGE REPORT{c['reset']}")
    lines.append(
        f"  Ran {total} tests in {duration:.1f}s | "
        f"{c['green']}{passed} passed{c['reset']} | "
        f"{c['red']}{failed} failed{c['reset']} | "
        f"{errors} errors"
    )
    lines.append(f"{c['bold']}{'=' * W}{c['reset']}")

    # Concern icons
    icons = {
        "COLLECTION": "\U0001f534",
        "UNIT": "\U0001f534",
        "INTEGRATION": "\U0001f7e1",
        "HARNESS": "\U0001f535",
        "OTHER": "\u26aa",
        "XFAIL": "\u2b1c",
    }

    total_failures = 0
    total_root_causes = 0
    bucket_summaries: list[tuple[str, str, int, int]] = []

    for concern, label, description in CONCERNS:
        groups = grouped.get(concern, [])
        test_count = sum(len(g.tests) for g in groups)
        root_causes = len(groups)

        total_failures += test_count
        total_root_causes += root_causes
        bucket_summaries.append((concern, label, test_count, root_causes))

        icon = icons.get(concern, "")
        color = c.get(concern, "")
        lines.append("")
        lines.append(
            f"{color}{icon} {concern} \u2014 {label} ({test_count} tests){c['reset']}"
        )
        lines.append(f"   {c['dim']}{description}{c['reset']}")

        lines.append(f"  \u250c{'─' * (W - 2)}\u2510")

        if not groups:
            lines.append(_box_line("(no failures)"))
        else:
            for gi, group in enumerate(groups):
                if gi > 0:
                    lines.append(f"  \u251c{'─' * (W - 2)}\u2524")

                # Error signature header
                display = group.display_message
                if len(display) > W - 6:
                    display = display[: W - 9] + "..."
                lines.append(_box_line(f"{color}{display}{c['reset']}"))

                count_text = f"({len(group.tests)} tests"
                if len(group.tests) > 1:
                    count_text += " \u2014 likely 1 root cause"
                count_text += ")"
                lines.append(_box_line(f"  {count_text}"))
                lines.append(_box_line(""))

                limit = max_tests if max_tests > 0 else len(group.tests)
                shown = group.tests[:limit]
                for t in shown:
                    # Truncate long node IDs
                    display_id = t
                    max_len = W - 10
                    if len(display_id) > max_len:
                        display_id = display_id[: max_len - 2] + ".."
                    lines.append(_box_line(f"  \u2022 {display_id}"))

                remaining = len(group.tests) - limit
                if remaining > 0:
                    lines.append(_box_line(f"  ... and {remaining} more"))

        lines.append(f"  \u2514{'─' * (W - 2)}\u2518")

    # Summary footer
    lines.append("")
    lines.append(f"{'─' * W}")
    lines.append(f"{c['bold']}  TRIAGE SUMMARY{c['reset']}")
    lines.append(f"{'─' * W}")

    for concern, label, test_count, root_causes in bucket_summaries:
        # Pad label to align counts
        padded_label = f"{label} ".ljust(26, ".")
        rc_text = (
            f"  ({root_causes} root cause{'s' if root_causes != 1 else ''})"
            if root_causes
            else ""
        )
        lines.append(f"  {concern}  {padded_label} {test_count}{rc_text}")

    lines.append(f"{'─' * W}")
    lines.append(
        f"  Root causes to fix: {c['bold']}{total_root_causes}{c['reset']} | "
        f"Total failures: {c['bold']}{total_failures}{c['reset']}"
    )

    # Suggest what to fix first
    for concern, label, test_count, root_causes in bucket_summaries:
        if root_causes > 0:
            lines.append(
                f"  {c['bold']}Fix the {root_causes} {concern} root cause{'s' if root_causes != 1 else ''} "
                f"first \u2014 {'it' if root_causes == 1 else 'they'} likely "
                f"unblock{'s' if root_causes == 1 else ''} {test_count} tests.{c['reset']}"
            )
            break

    lines.append(f"{c['bold']}{'=' * W}{c['reset']}")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    # Extract our own flags
    use_color = True
    report_file: str | None = None

    if "--no-color" in args:
        use_color = False
        args = [a for a in args if a != "--no-color"]

    # --report / --report=FILE
    filtered_args: list[str] = []
    for a in args:
        if a == "--report":
            report_file = "triage_report.txt"
        elif a.startswith("--report="):
            report_file = a.split("=", 1)[1]
        else:
            filtered_args.append(a)
    args = filtered_args

    # Auto-detect: no color if output is not a terminal
    if not sys.stdout.isatty() and "--color" not in args:
        use_color = False

    c = _colors(use_color)

    # Create a temp file for the JSON report
    report_fd, report_path = tempfile.mkstemp(suffix=".json", prefix="triage_")
    os.close(report_fd)

    try:
        # Build pytest command
        pytest_args = [
            sys.executable,
            "-m",
            "pytest",
            f"--json-report-file={report_path}",
            "--json-report",
            "--tb=long",
            "-q",
        ] + args

        print(f"{c['dim']}Running: {' '.join(pytest_args)}{c['reset']}")
        print()

        # Run pytest — let it print to stdout/stderr normally
        result = subprocess.run(pytest_args, cwd=str(Path(__file__).parent))

        # Parse the JSON report
        try:
            with open(report_path) as f:
                report = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"\n{c['red']}Error: Could not read JSON report: {exc}{c['reset']}")
            print(
                "Make sure pytest-json-report is installed: pip install pytest-json-report"
            )
            return 1

        # Build summary stats
        summary_data = report.get("summary", {})
        summary = {
            "total": summary_data.get("total", 0),
            "passed": summary_data.get("passed", 0),
            "failed": summary_data.get("failed", 0),
            "error": summary_data.get("error", 0),
            "duration": report.get("duration", 0.0),
        }

        # Parse and render
        grouped = parse_report(report)
        output = render_report(grouped, summary, c)

        print()
        print(output)

        # Write full (untruncated, no-color, wide) report to file
        if report_file:
            plain_c = _colors(False)
            full_output = render_report(
                grouped,
                summary,
                plain_c,
                max_tests=0,
                box_width=120,
            )
            out_path = Path(report_file)
            out_path.write_text(full_output + "\n", encoding="utf-8")
            print(
                f"\n{c['bold']}Full report written to: {out_path.resolve()}{c['reset']}"
            )

        # Exit code = number of collection + unit failures (capped at 125 for POSIX)
        collection_count = sum(len(g.tests) for g in grouped.get("COLLECTION", []))
        unit_count = sum(len(g.tests) for g in grouped.get("UNIT", []))
        critical = collection_count + unit_count
        return min(critical, 125) if critical > 0 else result.returncode

    finally:
        # Clean up temp file
        try:
            os.unlink(report_path)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
