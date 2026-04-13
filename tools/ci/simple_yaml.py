from __future__ import annotations

from typing import Any


def load_yaml(text: str) -> Any:
    tokens = _tokenize(text)
    if not tokens:
        return None
    return _parse_tokens(tokens, tokens[0][0])


def _tokenize(text: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        stripped = raw_line.lstrip(" ")
        if stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(stripped)
        tokens.append((indent, stripped.rstrip()))
    return tokens


def _parse_tokens(tokens: list[tuple[int, str]], indent: int) -> Any:
    if not tokens:
        return None
    if tokens[0][1].startswith("- "):
        return _parse_list(tokens, indent)
    return _parse_mapping(tokens, indent)


def _parse_list(tokens: list[tuple[int, str]], indent: int) -> list[Any]:
    items: list[Any] = []
    i = 0
    while i < len(tokens):
        line_indent, line = tokens[i]
        if line_indent != indent or not line.startswith("- "):
            raise ValueError(f"expected list item at indent {indent}, got {line!r}")
        content = line[2:].strip()
        j = i + 1
        while j < len(tokens):
            next_indent, next_line = tokens[j]
            if next_indent < indent:
                break
            if next_indent == indent and next_line.startswith("- "):
                break
            j += 1
        child = tokens[i + 1 : j]
        if not content:
            item = _parse_tokens(child, indent + 2) if child else None
        elif _looks_like_mapping_entry(content):
            item = _parse_tokens([(indent + 2, content), *child], indent + 2)
        else:
            item = _parse_scalar(content)
        items.append(item)
        i = j
    return items


def _parse_mapping(tokens: list[tuple[int, str]], indent: int) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    i = 0
    while i < len(tokens):
        line_indent, line = tokens[i]
        if line_indent != indent or line.startswith("- "):
            raise ValueError(f"expected mapping entry at indent {indent}, got {line!r}")
        key, sep, rest = line.partition(":")
        if not sep:
            raise ValueError(f"expected key/value mapping, got {line!r}")
        key = key.strip()
        rest = rest.lstrip()
        j = i + 1
        while j < len(tokens) and tokens[j][0] > indent:
            j += 1
        child = tokens[i + 1 : j]
        if rest == ">":
            mapping[key] = _fold_block(child)
        elif rest == "":
            mapping[key] = _parse_tokens(child, indent + 2) if child else None
        else:
            mapping[key] = _parse_scalar(rest)
        i = j
    return mapping


def _fold_block(tokens: list[tuple[int, str]]) -> str:
    return " ".join(line.strip() for _indent, line in tokens).strip()


def _looks_like_mapping_entry(content: str) -> bool:
    return content.endswith(":") or ": " in content


def _parse_scalar(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
        return None
    if value.isdigit():
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value
