from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_VERBS = ("make", "define", "derive", "provide")


@dataclass(frozen=True, slots=True)
class FactoryCandidate:
    path: Path
    name: str
    qualname: str
    form: str
    async_mode: str
    line: int


def _is_factory_name(name: str) -> bool:
    lowered = name.lower()
    return any(lowered == verb or lowered.startswith(verb + "_") for verb in _VERBS) or any(
        name.startswith(verb) and len(name) > len(verb) and name[len(verb)].isupper()
        for verb in _VERBS
    )


def _descriptor(node: ast.FunctionDef | ast.AsyncFunctionDef, in_class: bool) -> str:
    decorators = {
        decorator.id
        for decorator in node.decorator_list
        if isinstance(decorator, ast.Name)
    }
    if "classmethod" in decorators:
        return "classmethod"
    if "staticmethod" in decorators:
        return "staticmethod"
    return "instance-method" if in_class else "function"


def discover_factory_candidates(paths: Iterable[str | Path]) -> tuple[FactoryCandidate, ...]:
    discovered: list[FactoryCandidate] = []
    for supplied in paths:
        path = Path(supplied)
        files = path.rglob("*.py") if path.is_dir() else (path,)
        for source_path in files:
            tree = ast.parse(source_path.read_text(encoding="utf-8-sig"), filename=str(source_path))
            for parent in ast.walk(tree):
                if not isinstance(parent, (ast.Module, ast.ClassDef)):
                    continue
                for node in parent.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_factory_name(node.name):
                        in_class = isinstance(parent, ast.ClassDef)
                        qualname = f"{parent.name}.{node.name}" if in_class else node.name
                        discovered.append(
                            FactoryCandidate(
                                path=source_path,
                                name=node.name,
                                qualname=qualname,
                                form=_descriptor(node, in_class),
                                async_mode="async" if isinstance(node, ast.AsyncFunctionDef) else "sync",
                                line=node.lineno,
                            )
                        )
                    elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                        targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
                        for target in targets:
                            if isinstance(target, ast.Name) and _is_factory_name(target.id):
                                discovered.append(
                                    FactoryCandidate(
                                        path=source_path,
                                        name=target.id,
                                        qualname=target.id,
                                        form="alias",
                                        async_mode="unknown",
                                        line=node.lineno,
                                    )
                                )
    return tuple(sorted(discovered, key=lambda item: (str(item.path), item.line, item.name)))
