"""Resolve subscription scalar policy through the same model on every surface."""

from dataclasses import asdict, fields
import os
from pathlib import Path
from .quotas import SubscriptionPolicy

POLICY_FIELDS = tuple(f.name for f in fields(SubscriptionPolicy))
STRING_FIELDS = {"store", "store_url_env", "namespace", "scope"}


def read_toml(path):
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    with Path(path).open("rb") as stream:
        return tomllib.load(stream)


def policy_value(name, value):
    if name in STRING_FIELDS:
        return value
    if not isinstance(value, str):
        return value
    if name.startswith("max_") or "_burst_" in name:
        return int(value)
    return float(value)


def resolve_subscription_policy(
    *, config_file=None, environ=None, overrides=None, defaults=None, authoritative=None
):
    if authoritative is not None:
        if config_file is not None or overrides:
            raise ValueError(
                "authoritative subscription policy cannot be combined with file or explicit overrides"
            )
        if not isinstance(authoritative, SubscriptionPolicy):
            raise TypeError("authoritative policy must be SubscriptionPolicy")
        return authoritative, {name: "python-config" for name in POLICY_FIELDS}
    values = asdict(defaults or SubscriptionPolicy())
    provenance = {name: "default" for name in values}
    if config_file:
        document = read_toml(config_file)
        block = document.get("subscriptions", {})
        if not isinstance(block, dict):
            raise ValueError("subscriptions must be a TOML table")
        unknown = set(block) - set(POLICY_FIELDS)
        if unknown:
            raise ValueError(
                "unknown subscription fields: " + ",".join(sorted(unknown))
            )
        for name, value in block.items():
            values[name] = value
            provenance[name] = "toml"
    env = os.environ if environ is None else environ
    unknown_env = {
        name
        for name in env
        if name.startswith("TIGRBL_SUBSCRIPTIONS_")
        and name.removeprefix("TIGRBL_SUBSCRIPTIONS_").lower() not in POLICY_FIELDS
    }
    if unknown_env:
        raise ValueError(
            "unknown subscription environment fields: " + ",".join(sorted(unknown_env))
        )
    for name in POLICY_FIELDS:
        key = "TIGRBL_SUBSCRIPTIONS_" + name.upper()
        if key in env:
            values[name] = policy_value(name, env[key])
            provenance[name] = "environment"
    for name, value in (overrides or {}).items():
        if name not in POLICY_FIELDS:
            raise ValueError("unknown subscription override: " + name)
        if value is not None:
            values[name] = policy_value(name, value)
            provenance[name] = "explicit"
    return SubscriptionPolicy(**values), provenance
