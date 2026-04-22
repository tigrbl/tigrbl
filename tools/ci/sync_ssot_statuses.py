from __future__ import annotations

import sys

from ssot_authority_model import main


if __name__ == "__main__":
    if "--mode" not in sys.argv:
        sys.argv[1:1] = ["--mode", "sync"]
    main()
