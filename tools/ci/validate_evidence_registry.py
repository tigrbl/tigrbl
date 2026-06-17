from __future__ import annotations

from common import fail
from ssot_legacy_authority import legacy_claim_rows, validate_claim_links


def main() -> None:
    rows = legacy_claim_rows()
    errors = validate_claim_links(rows)
    if not rows:
        errors.append('.ssot/registry.json must contain legacy conformance claim rows')

    fail(errors)
    print('SSOT evidence linkage validation passed')


if __name__ == '__main__':
    main()
