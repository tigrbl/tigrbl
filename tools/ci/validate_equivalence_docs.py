from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from common import fail, repo_root

ROOT = repo_root()
sys.path.insert(0, str(ROOT / "tools" / "docs"))

from update_equivalence_docs import check_docs  # noqa: E402


def main() -> None:
    errors = check_docs()
    fail(errors)
    print("equivalence docs validation passed")


if __name__ == "__main__":
    main()
