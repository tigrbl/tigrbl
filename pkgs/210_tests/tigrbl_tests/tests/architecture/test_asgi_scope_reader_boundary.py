from __future__ import annotations

import ast
from pathlib import Path


_PACKAGES = {
    "020_base": ("tigrbl_base",),
    "040_atoms": ("tigrbl_atoms",),
    "045_kernel": ("tigrbl_kernel",),
    "050_runtime": ("tigrbl_runtime",),
    "070_concrete": ("tigrbl_concrete",),
    "080_facade": ("tigrbl",),
}
_SCOPE_NAMES = {"scope", "raw_scope", "scope_dict", "asgi_scope", "_scope"}


def _literal(node, value):
    return isinstance(node, ast.Constant) and node.value == value


def _scope_expression(node, names):
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, ast.Attribute):
        return node.attr in _SCOPE_NAMES
    if isinstance(node, ast.Subscript):
        return _literal(node.slice, "scope")
    if isinstance(node, ast.BoolOp):
        return any(_scope_expression(value, names) for value in node.values)
    if isinstance(node, ast.Call) and node.args:
        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            return len(node.args) >= 2 and _literal(node.args[1], "scope")
        if isinstance(node.func, ast.Name) and node.func.id == "dict":
            return _scope_expression(node.args[0], names)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "get":
                return _literal(node.args[0], "scope")
            return _scope_expression(node.args[0], names)
    return False


def _scope_read_lines(tree, *, owner=False):
    allowed = {
        descendant
        for statement in tree.body
        if owner
        and isinstance(statement, ast.FunctionDef)
        and statement.name == "_read_scope_type"
        for descendant in ast.walk(statement)
    }
    reads = set()
    for function in ast.walk(tree):
        if not isinstance(
            function, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        pending = list(function.body)
        nodes = []
        while pending:
            node = pending.pop()
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
            ):
                continue
            nodes.append(node)
            pending.extend(ast.iter_child_nodes(node))
        names = set(_SCOPE_NAMES)
        while True:
            count = len(names)
            for node in nodes:
                if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                    targets = (
                        node.targets if isinstance(node, ast.Assign) else (node.target,)
                    )
                    if _scope_expression(node.value, names):
                        names.update(
                            target.id
                            for target in targets
                            if isinstance(target, ast.Name)
                        )
            if count == len(names):
                break
        for node in nodes:
            if node in allowed:
                continue
            if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
                if _literal(node.slice, "type") and _scope_expression(
                    node.value, names
                ):
                    reads.add(node.lineno)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.args
            ):
                if node.func.attr in {"get", "pop", "setdefault", "__getitem__"}:
                    if _literal(node.args[0], "type") and _scope_expression(
                        node.func.value, names
                    ):
                        reads.add(node.lineno)
            if isinstance(node, ast.Match) and _scope_expression(node.subject, names):
                for case in node.cases:
                    for pattern in ast.walk(case.pattern):
                        if isinstance(pattern, ast.MatchMapping) and any(
                            _literal(key, "type") for key in pattern.keys
                        ):
                            reads.add(pattern.lineno)
    return reads


def test_raw_asgi_scope_type_has_one_reader():
    packages = Path(__file__).resolve().parents[4]
    violations = []
    for layer, names in _PACKAGES.items():
        for name in names:
            source = packages / layer / name / name
            assert source.is_dir(), source
            for file in sorted(source.rglob("*.py")):
                tree = ast.parse(file.read_text(encoding="utf-8-sig"))
                owner = name == "tigrbl_atoms" and file == source / "protocol_scope.py"
                violations.extend(
                    f"{file.relative_to(packages)}:{line}"
                    for line in sorted(_scope_read_lines(tree, owner=owner))
                )
    assert not violations, "\n".join(violations)


def test_scope_reader_guard_tracks_aliases_and_mapping_patterns():
    tree = ast.parse(
        "def dispatch(envelope, message):\n"
        "    incoming = envelope.scope\n"
        "    copied = dict(incoming)\n"
        '    copied.get("type")\n'
        '    incoming["type"]\n'
        "    match copied:\n"
        '        case {"type": kind}:\n'
        "            pass\n"
        '    message["type"]\n'
    )
    assert _scope_read_lines(tree) == {4, 5, 7}
