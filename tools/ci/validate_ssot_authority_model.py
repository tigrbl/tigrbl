from __future__ import annotations

from common import fail
from ssot_authority_model import load_registry, validate_authority_model


def main() -> None:
    fail(validate_authority_model(load_registry()))


if __name__ == "__main__":
    main()
