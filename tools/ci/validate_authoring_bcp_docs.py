from __future__ import annotations

from pathlib import Path
import re

from common import fail, repo_root

ROOT = repo_root()

BCP_DOC = ROOT / "docs" / "developer" / "AUTHORING_BCP.md"
ROOT_README = ROOT / "README.md"
FACADE_README = ROOT / "pkgs" / "core" / "tigrbl" / "README.md"
BCP_TITLE = "Convenient Authoring Path and Best Current Practice (BCP)"
README_BCP_HEADING = f"## {BCP_TITLE}"

REQUIRED_DOCS = [
    BCP_DOC,
    ROOT_README,
    FACADE_README,
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "developer" / "README.md",
    ROOT / "docs" / "developer" / "CI_VALIDATION.md",
    ROOT / "docs" / "governance" / "DOC_POINTERS.md",
]

REQUIRED_BCP_PHRASES = [
    f"# {BCP_TITLE}",
    "Do:",
    "Do not:",
    "Avoid:",
    "FastAPI",
    "Starlette",
    "Flask",
    "SSE",
    "WebSocket",
    "WebTransport",
    "mapped_column",
    "Column(...)",
    "flush()",
    "commit()",
    "Allowed Exceptions",
    "Why:",
]

MAIN_README_REQUIRED_PHRASES = [
    README_BCP_HEADING,
    "docs/developer/AUTHORING_BCP.md",
    "Do:",
    "Do not:",
    "Avoid:",
    "FastAPI",
    "Starlette",
    "Flask",
    "SSE",
    "WebSocket",
    "WebTransport",
    "mapped_column",
    "Column(...)",
    "Why:",
]

BOUNDARY_README_REQUIREMENTS = {
    Path("pkgs/core/tigrbl_core/README.md"): [
        "Authoring BCP for this boundary:",
        "Do treat `ColumnSpec`",
        "Do not move application route authoring",
        "Avoid duplicating spec fields",
    ],
    Path("pkgs/core/tigrbl_base/README.md"): [
        "Authoring BCP for this boundary:",
        "Do use `tigrbl-base`",
        "Do not put route registration side effects",
        "Avoid treating SQLAlchemy materialization",
    ],
    Path("pkgs/core/tigrbl_concrete/README.md"): [
        "Authoring BCP for this boundary:",
        "Do use `tigrbl-concrete`",
        "Do not teach application users",
        "Avoid hard-coded documentation",
    ],
    Path("pkgs/core/tigrbl_runtime/README.md"): [
        "Runtime authoring BCP:",
        "Do use this package for runtime-owned routing",
        "Do not bypass kernel plans",
        "Avoid hiding behavior",
    ],
    Path("pkgs/core/tigrbl_orm/README.md"): [
        README_BCP_HEADING,
        "- Do:",
        "- Do not:",
        "- Avoid:",
        "mapped_column",
        "Column(...)",
    ],
}

CODE_FENCE_RE = re.compile(r"```(?:[A-Za-z0-9_+\-.]*)\n(.*?)```", re.DOTALL)

PROHIBITED_APPLICATION_SNIPPETS = {
    "FastAPI route authoring": re.compile(
        r"\bfrom\s+fastapi\s+import\b|\bimport\s+fastapi\b|\bFastAPI\s*\(|\bAPIRouter\s*\(",
        re.MULTILINE,
    ),
    "Starlette route authoring": re.compile(
        r"\bfrom\s+starlette\b|\bimport\s+starlette\b|\bRoute\s*\(",
        re.MULTILINE,
    ),
    "Flask route authoring": re.compile(
        r"\bfrom\s+flask\s+import\b|\bimport\s+flask\b|\bFlask\s*\(|\bBlueprint\s*\(|\bMethodView\b",
        re.MULTILINE,
    ),
    "raw SQLAlchemy mapped_column authoring": re.compile(
        r"\bmapped_column\s*\(",
        re.MULTILINE,
    ),
    "raw SQLAlchemy Column authoring": re.compile(
        r"\bfrom\s+sqlalchemy\s+import\s+.*\bColumn\b|\bColumn\s*\(",
        re.MULTILINE,
    ),
    "direct DB/session transaction call": re.compile(
        r"\.(?:flush|commit)\s*\(",
        re.MULTILINE,
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _authoring_bcp_section(text: str) -> str:
    marker = README_BCP_HEADING
    start = text.find(marker)
    if start == -1:
        return text
    end = text.find("\n## ", start + len(marker))
    if end == -1:
        return text[start:]
    return text[start:end]


def _guidance_groups(text: str) -> list[tuple[str, str]]:
    groups: list[tuple[str, str]] = []
    active_heading: str | None = None
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if active_heading is not None:
            groups.append((active_heading, "\n".join(current).strip()))
        current = []

    for line in text.splitlines():
        if line.startswith("### "):
            flush()
            active_heading = line[4:].strip()
            continue
        if line.startswith("## "):
            flush()
            active_heading = None
            continue
        if active_heading is not None:
            current.append(line)

    flush()
    return groups


def _validate_grouped_guidance(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    groups = _guidance_groups(text)
    if not groups:
        return [f"{rel} has no grouped BCP guidance sections"]

    for heading, body in groups:
        if "- Do:" not in body:
            errors.append(f"{rel} group {heading!r} missing '- Do:' bullet")
        if "- Why:" not in body:
            errors.append(f"{rel} group {heading!r} missing '- Why:' bullet")
        if "- Avoid:" not in body and "- Do not:" not in body:
            errors.append(
                f"{rel} group {heading!r} missing '- Avoid:' or '- Do not:' bullet"
            )
    return errors


def _active_package_readmes() -> list[Path]:
    patterns = [
        "pkgs/core/*/README.md",
        "pkgs/engines/*/README.md",
        "pkgs/apps/*/README.md",
    ]
    readmes: list[Path] = []
    for pattern in patterns:
        readmes.extend(ROOT.glob(pattern))
    return sorted(path for path in readmes if path.is_file())


def _app_facing_readmes() -> list[Path]:
    return sorted({ROOT_README, FACADE_README, *_active_package_readmes()})


def main() -> None:
    errors: list[str] = []

    for doc in REQUIRED_DOCS:
        if not doc.is_file():
            errors.append(f"missing authoring BCP document or pointer {doc.relative_to(ROOT)}")

    if errors:
        fail(errors)

    bcp_text = _read(BCP_DOC)
    for phrase in REQUIRED_BCP_PHRASES:
        if phrase not in bcp_text:
            errors.append(f"{BCP_DOC.relative_to(ROOT)} missing required phrase {phrase!r}")

    for readme in [ROOT_README, FACADE_README]:
        text = _read(readme)
        for phrase in MAIN_README_REQUIRED_PHRASES:
            if phrase not in text:
                errors.append(f"{readme.relative_to(ROOT)} missing required BCP phrase {phrase!r}")

    grouped_guidance_targets = {
        BCP_DOC: bcp_text,
        ROOT_README: _authoring_bcp_section(_read(ROOT_README)),
        FACADE_README: _authoring_bcp_section(_read(FACADE_README)),
    }
    for path, text in grouped_guidance_targets.items():
        errors.extend(_validate_grouped_guidance(path, text))

    for rel, phrases in BOUNDARY_README_REQUIREMENTS.items():
        path = ROOT / rel
        text = _read(path)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel} missing boundary BCP phrase {phrase!r}")

    for readme in _app_facing_readmes():
        rel = readme.relative_to(ROOT)
        text = _read(readme)
        for index, block in enumerate(CODE_FENCE_RE.findall(text), start=1):
            for label, pattern in PROHIBITED_APPLICATION_SNIPPETS.items():
                if pattern.search(block):
                    errors.append(
                        f"{rel} code block {index} teaches prohibited application "
                        f"authoring pattern: {label}"
                    )

    fail(errors)
    print("authoring BCP docs validation passed")


if __name__ == "__main__":
    main()
