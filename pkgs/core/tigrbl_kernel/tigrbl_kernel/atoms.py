from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    cast,
)

from tigrbl_typing.phases import HOOK_PHASES as HOOK_PHASES

from tigrbl_atoms import StepFn
from . import events as _ev, ordering as _ordering

logger = logging.getLogger(__name__)

_AtomRun = Callable[[Optional[object], Any], Any]
_DiscoveredAtom = tuple[str, _AtomRun]
_COMPILED_PARAM_SKIP_ATOM_NAMES = frozenset(
    {
        "ingress.transport_extract",
        "ingress.input_prepare",
        "dispatch.binding_match",
        "dispatch.binding_parse",
        "dispatch.input_normalize",
        "wire.build_in",
        "wire.validate_in",
        "resolve.assemble",
        "sys.phase_db",
    }
)
_COMPILED_PHASE_DB_REQUIRED_ATOM_NAMES = frozenset(
    {
        "sys.start_tx",
        "sys.commit_tx",
    }
)


def _is_async_callable(run: _AtomRun) -> bool:
    if inspect.iscoroutinefunction(run):
        return True
    call = getattr(run, "__call__", None)
    return inspect.iscoroutinefunction(call)


def _discover_atoms() -> list[_DiscoveredAtom]:
    out: list[_DiscoveredAtom] = []
    try:
        import tigrbl_atoms.atoms as atoms_pkg  # type: ignore
    except Exception:
        return out

    for info in pkgutil.walk_packages(atoms_pkg.__path__, atoms_pkg.__name__ + "."):  # type: ignore[attr-defined]
        if info.ispkg:
            continue
        try:
            mod = importlib.import_module(info.name)
            instance = getattr(mod, "INSTANCE", None)
            if instance is not None and callable(instance):
                anchor = getattr(instance, "anchor", None) or getattr(
                    mod, "ANCHOR", None
                )
                if isinstance(anchor, str):
                    out.append((anchor, cast(_AtomRun, instance)))
                    continue
            anchor = getattr(mod, "ANCHOR", None)
            run = getattr(mod, "run", None)
            if isinstance(anchor, str) and callable(run):
                out.append((anchor, cast(_AtomRun, run)))
        except Exception:
            continue
    logger.debug("kernel: discovered %d atoms", len(out))
    return out


def _infer_domain_subject(run: _AtomRun) -> tuple[Optional[str], Optional[str]]:
    mod = getattr(run, "__module__", "") or ""
    parts = mod.split(".")
    try:
        i = parts.index("atoms")
        return (
            parts[i + 1] if i + 1 < len(parts) else None,
            parts[i + 2] if i + 2 < len(parts) else None,
        )
    except ValueError:
        return None, None


def _make_label(anchor: str, run: _AtomRun) -> Optional[str]:
    domain, subject = _infer_domain_subject(run)
    return f"atom:{domain}:{subject}@{anchor}" if (domain and subject) else None


def _policy_atom_name(
    run: _AtomRun, direct_run: _AtomRun, label: Optional[str]
) -> Optional[str]:
    for candidate in (
        run,
        getattr(run, "__self__", None),
        getattr(run, "__call__", None),
        direct_run,
        getattr(direct_run, "__self__", None),
        getattr(direct_run, "__call__", None),
    ):
        for attr in ("__tigrbl_atom_name__", "__tigrbl_name__", "name"):
            value = getattr(candidate, attr, None)
            if isinstance(value, str) and value:
                return value
    if isinstance(label, str) and label:
        prefix = label.split("@", 1)[0]
        if prefix.startswith("atom:"):
            return prefix.split("atom:", 1)[1].replace(":", ".")
        if ":hook:wire:" in prefix:
            return prefix.split(":hook:wire:", 1)[1].replace(":", ".")
        return prefix.replace(":", ".")
    return None


def _use_two_args_for(run: _AtomRun) -> bool:
    try:
        params = tuple(inspect.signature(run).parameters.values())
        positional = [
            p
            for p in params
            if p.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
        return len(positional) != 1
    except (TypeError, ValueError):
        return True


def _preferred_direct_run(run: _AtomRun) -> _AtomRun:
    preferred = getattr(run, "__tigrbl_hot_run__", None)
    if callable(preferred):
        return cast(_AtomRun, preferred)

    call = getattr(run, "__call__", None)
    preferred = getattr(call, "__tigrbl_hot_run__", None)
    if callable(preferred):
        return cast(_AtomRun, preferred)

    module = inspect.getmodule(run)
    if module is None:
        module_name = getattr(run, "__module__", None) or getattr(type(run), "__module__", None)
        if isinstance(module_name, str):
            try:
                module = importlib.import_module(module_name)
            except Exception:
                module = None
    if module is not None:
        candidate = getattr(module, "_run", None)
        if callable(candidate):
            return cast(_AtomRun, candidate)
        candidate = getattr(module, "run", None)
        if callable(candidate):
            return cast(_AtomRun, candidate)
    return run


def _wrap_atom(run: _AtomRun, *, anchor: str) -> StepFn:
    use_two_args = _use_two_args_for(run)
    direct_run = _preferred_direct_run(run)
    direct_use_two_args = _use_two_args_for(direct_run)

    async def _step(ctx: Any) -> Any:
        rv = run(None, ctx) if use_two_args else run(ctx)  # type: ignore[misc]
        if inspect.isawaitable(rv):
            return await cast(Any, rv)
        return rv

    label = getattr(run, "__tigrbl_label", None)
    if not isinstance(label, str):
        label = _make_label(anchor, run)
    atom_name = _policy_atom_name(run, direct_run, label)
    if label:
        setattr(_step, "__tigrbl_label", label)
    if atom_name:
        setattr(_step, "__tigrbl_atom_name__", atom_name)
    setattr(_step, "__tigrbl_direct_run", direct_run)
    setattr(_step, "__tigrbl_use_two_args", direct_use_two_args)
    setattr(_step, "__tigrbl_has_direct_dep", False)
    setattr(_step, "__tigrbl_direct_is_async", _is_async_callable(direct_run))
    setattr(
        _step,
        "__tigrbl_skip_in_compiled_param",
        bool(atom_name in _COMPILED_PARAM_SKIP_ATOM_NAMES),
    )
    setattr(
        _step,
        "__tigrbl_requires_phase_db",
        bool(atom_name in _COMPILED_PHASE_DB_REQUIRED_ATOM_NAMES),
    )
    return _step


def _hook_phase_chains(model: type, alias: str) -> Dict[str, List[StepFn]]:
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, List[StepFn]] = {ph: [] for ph in HOOK_PHASES}
    if alias_ns is None:
        return out
    for phase in HOOK_PHASES:
        out[phase] = list(getattr(alias_ns, phase, []) or [])
    return out


def _is_persistent(chains: Mapping[str, Sequence[StepFn]]) -> bool:
    for fn in chains.get("START_TX", ()) or ():
        if getattr(fn, "__name__", "") == "start_tx":
            return True
    for fn in chains.get("PRE_TX_BEGIN", ()) or ():
        if getattr(fn, "__name__", "") == "mark_skip_persist":
            return False
    return False


def _label_dep_atom(*, kind: str, index: int, anchor: str) -> str:
    return f"hook:dep:{kind}:{index}@{anchor}"


def _make_dep_atom_step(run_fn: _AtomRun, dep: Any, *, label: str) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = run_fn(dep, ctx)
        if hasattr(rv, "__await__"):
            return await cast(Any, rv)
        return rv

    setattr(_step, "__tigrbl_label", label)
    setattr(_step, "__tigrbl_direct_run", run_fn)
    setattr(_step, "__tigrbl_direct_dep", dep)
    setattr(_step, "__tigrbl_use_two_args", True)
    setattr(_step, "__tigrbl_has_direct_dep", True)
    setattr(_step, "__tigrbl_direct_is_async", _is_async_callable(run_fn))
    setattr(_step, "__tigrbl_skip_in_compiled_param", False)
    setattr(_step, "__tigrbl_requires_phase_db", False)
    return _step


def _inject_pre_tx_dep_atoms(chains: Dict[str, List[StepFn]], sp: Any | None) -> None:
    if sp is None:
        return
    try:
        from tigrbl_atoms.atoms.dep.security import INSTANCE as sec_run  # type: ignore
        from tigrbl_atoms.atoms.dep.extra import INSTANCE as dep_run  # type: ignore
    except Exception:
        try:
            from tigrbl_atoms.atoms.dep.security import run as sec_run  # type: ignore
            from tigrbl_atoms.atoms.dep.extra import run as dep_run  # type: ignore
        except Exception:
            return

    pre_tx = chains.setdefault("PRE_TX_BEGIN", [])
    for idx, dep in enumerate(getattr(sp, "secdeps", ()) or ()):
        pre_tx.append(
            _make_dep_atom_step(
                sec_run,
                dep,
                label=_label_dep_atom(
                    kind="security", index=idx, anchor=_ev.DEP_SECURITY
                ),
            )
        )
    for idx, dep in enumerate(getattr(sp, "deps", ()) or ()):
        pre_tx.append(
            _make_dep_atom_step(
                dep_run,
                dep,
                label=_label_dep_atom(kind="extra", index=idx, anchor=_ev.DEP_EXTRA),
            )
        )


def _inject_atoms(
    chains: Dict[str, List[StepFn]],
    atoms: Iterable[_DiscoveredAtom],
    *,
    persistent: bool,
    target: str | None = None,
) -> None:
    order = {name: i for i, name in enumerate(_ev.all_events_ordered())}

    def _sort_key(item: _DiscoveredAtom) -> tuple[int, int]:
        anchor, run = item
        anchor_idx = order.get(anchor, 10_000)
        domain, subject = _infer_domain_subject(run)
        token = f"{domain}:{subject}" if domain and subject else ""
        pref = _ordering._PREF.get(anchor, ())
        token_idx = pref.index(token) if token in pref else 10_000
        return anchor_idx, token_idx

    for anchor, run in sorted(atoms, key=_sort_key):
        if _ev.is_valid_event(anchor):
            info = _ev.get_anchor_info(anchor)
            phase = info.phase
            persist_tied = info.persist_tied
        elif anchor == "INGRESS_ROUTE":
            # Back-compat phase alias retained for route-stage atom injection.
            phase = "INGRESS_ROUTE"
            persist_tied = False
        elif anchor in _ev.PHASES:
            phase = anchor
            persist_tied = False
        elif anchor == "INGRESS_ROUTE":
            # Compatibility alias retained for tests and legacy direct callers.
            # Canonical runtime ingress routing phase is INGRESS_DISPATCH.
            phase = anchor
            persist_tied = False
        else:
            continue

        domain, _subject = _infer_domain_subject(run)
        if not persistent and persist_tied:
            if not (
                domain == "sys"
                and isinstance(_subject, str)
                and _subject.startswith("handler_")
            ):
                continue
        if (
            domain == "sys"
            and isinstance(_subject, str)
            and _subject.startswith("handler_")
        ):
            handler_target = _subject.removeprefix("handler_")
            if handler_target != "persistence" and target and handler_target != target:
                continue
        if domain == "dep":
            continue

        chains.setdefault(phase, []).append(_wrap_atom(run, anchor=anchor))
