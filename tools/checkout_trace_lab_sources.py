"""Prepare only the public source files needed by the full transport example."""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / ".sources" / "trace-lab"
CHECKOUTS = {
    "tigrcorn": (
        "264c911970d9e25f97b8959ce4d16ac9e65f4c2b",
        ["/src/", "/pkgs/", "/tests/fixtures_third_party/"],
    ),
    "tigr-asgi-contract": (
        "19021714165c31bbe3a470ea0e1887761b0f9fbc",
        ["/packages/contract-py/src/"],
    ),
}


def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, (revision, sparse_paths) in CHECKOUTS.items():
        path = SOURCES / name
        subprocess.run(["git", "init", str(path)], check=True)
        git = ["git", "-c", "core.longpaths=true", "-C", str(path)]
        subprocess.run(
            [*git, "sparse-checkout", "set", "--no-cone", *sparse_paths], check=True
        )
        subprocess.run(
            [
                *git,
                "fetch",
                "--depth",
                "1",
                f"https://github.com/tigrbl/{name}.git",
                revision,
            ],
            check=True,
        )
        subprocess.run([*git, "checkout", "--detach", "FETCH_HEAD"], check=True)


if __name__ == "__main__":
    main()
