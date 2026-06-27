from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_VERSION_RE = re.compile(r'(?m)^(version\s*=\s*)"([^"]+)"')
PACKAGE_SPLIT_RE = re.compile(r"[\s,]+")
PYTHON_VERSION_FLOOR = "0.4.0.dev1"
PYPI_TRUSTED_PUBLISH_EXCLUDED = {}


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    dev: int | None = None

    @classmethod
    def parse(cls, value: str) -> "Version":
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:\.dev(\d+))?", value)
        if not match:
            raise ValueError(f"unsupported version {value!r}")
        major, minor, patch, dev = match.groups()
        return cls(
            int(major),
            int(minor),
            int(patch),
            int(dev) if dev is not None else None,
        )

    def bump(self, semver: str) -> "Version":
        segment = semver.lower()
        if segment in {"w", "major"}:
            raise ValueError("w/major bumps are disallowed in the release workflow")
        if segment in {"x", "minor"}:
            segment = "minor"
        elif segment in {"y", "patch"}:
            segment = "patch"
        elif segment in {"z", "dev"}:
            segment = "dev"

        if segment == "finalize":
            if self.dev is None:
                return self
            return Version(self.major, self.minor, self.patch)
        if segment == "minor":
            return Version(self.major, self.minor + 1, 0, 1)
        if segment in {"patch", "dev"}:
            if self.dev is None:
                return Version(self.major, self.minor, self.patch + 1, 1)
            return Version(self.major, self.minor, self.patch, self.dev + 1)
        raise ValueError(f"unsupported semver bump action {semver!r}")

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.dev is None:
            return base
        return f"{base}.dev{self.dev}"

    def is_less_than(self, other: "Version") -> bool:
        left = (self.major, self.minor, self.patch)
        right = (other.major, other.minor, other.patch)
        if left != right:
            return left < right
        if self.dev is None:
            return False
        if other.dev is None:
            return True
        return self.dev < other.dev

    def is_greater_than(self, other: "Version") -> bool:
        return other.is_less_than(self)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    old = read(path)
    if old == text:
        return False
    path.write_text(text, encoding="utf-8", newline="")
    return True


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def python_projects() -> list[dict[str, str]]:
    projects: list[dict[str, str]] = []
    for pyproject in sorted(ROOT.glob("pkgs/*/*/pyproject.toml")):
        text = read(pyproject)
        name_match = re.search(r'(?m)^name\s*=\s*"([^"]+)"', text)
        version_match = PYPROJECT_VERSION_RE.search(text)
        if not name_match or not version_match:
            continue
        projects.append(
            {
                "name": name_match.group(1),
                "version": version_match.group(2),
                "path": relative(pyproject),
            }
        )
    return projects


def parse_package_selection(value: str | None) -> set[str] | None:
    if value is None:
        return None
    selected = {item for item in PACKAGE_SPLIT_RE.split(value.strip()) if item}
    if not selected or selected == {"all"}:
        return None
    if "all" in selected:
        raise ValueError("package selection must be 'all' or a package list, not both")
    return selected


def filter_projects(
    projects: list[dict[str, str]], selected: set[str] | None
) -> list[dict[str, str]]:
    if selected is None:
        return projects
    return [project for project in projects if project["name"] in selected]


def validate_package_selection(
    selected: set[str] | None,
    py_projects: list[dict[str, str]],
) -> None:
    if selected is None:
        return
    known = {project["name"] for project in py_projects}
    unknown = selected.difference(known)
    if unknown:
        known_list = ", ".join(sorted(known))
        unknown_list = ", ".join(sorted(unknown))
        raise ValueError(f"unknown package(s): {unknown_list}. Known packages: {known_list}")


def ensure_allowed_target_version(
    name: str,
    old_version: str,
    new_version: str,
) -> None:
    old = Version.parse(old_version)
    new = Version.parse(new_version)
    floor = Version.parse(PYTHON_VERSION_FLOOR)
    if new.is_less_than(floor):
        raise ValueError(
            f"{name} target version {new_version} is below the required floor "
            f"{PYTHON_VERSION_FLOOR}"
        )
    if old.is_greater_than(new):
        raise ValueError(
            f"{name} target version {new_version} would downversion current "
            f"version {old_version}"
        )


def ensure_all_versions_meet_floor(
    all_py_projects: list[dict[str, str]],
    py_releases: list[dict[str, str]],
) -> None:
    planned_python = {release["name"]: release["version"] for release in py_releases}
    for project in all_py_projects:
        target_version = planned_python.get(project["name"], project["version"])
        ensure_allowed_target_version(
            project["name"],
            project["version"],
            target_version,
        )


def replace_python_version(path: Path, new_version: str) -> bool:
    text = read(path)
    updated, count = PYPROJECT_VERSION_RE.subn(rf'\g<1>"{new_version}"', text, count=1)
    if count != 1:
        raise RuntimeError(f"project version not found in {path}")
    return write_if_changed(path, updated)


def build_plan(
    semver: str, *, write_changes: bool, packages: str | None = None
) -> dict[str, object]:
    all_py_projects = python_projects()
    selected = parse_package_selection(packages)
    validate_package_selection(selected, all_py_projects)
    py_projects = filter_projects(all_py_projects, selected)
    changed: list[str] = []

    py_releases: list[dict[str, str]] = []
    for project in py_projects:
        new_version = str(Version.parse(project["version"]).bump(semver))
        ensure_allowed_target_version(project["name"], project["version"], new_version)
        py_releases.append({**project, "old_version": project["version"], "version": new_version})
        if write_changes and replace_python_version(ROOT / project["path"], new_version):
            changed.append(project["path"])

    all_releases = [
        {"kind": "pypi", "tag": f'{release["name"]}=={release["version"]}', **release}
        for release in py_releases
    ]
    pypi_releases = [
        release
        for release in py_releases
        if release["name"] not in PYPI_TRUSTED_PUBLISH_EXCLUDED
    ]
    pypi_skipped = [
        {
            "name": release["name"],
            "version": release["version"],
            "reason": PYPI_TRUSTED_PUBLISH_EXCLUDED[release["name"]],
        }
        for release in py_releases
        if release["name"] in PYPI_TRUSTED_PUBLISH_EXCLUDED
    ]

    is_prerelease = any(Version.parse(release["version"]).dev is not None for release in all_releases)
    ensure_all_versions_meet_floor(all_py_projects, py_releases)

    return {
        "semver": semver,
        "prerelease": is_prerelease,
        "package_selection": sorted(selected) if selected is not None else "all",
        "python": py_releases,
        "pypi": pypi_releases,
        "pypi_skipped": pypi_skipped,
        "github_releases": all_releases,
        "changed_files": sorted(set(changed)),
    }


def matrix_output(plan_path: Path, *, python_versions: str, output: Path | None) -> None:
    plan = json.loads(read(plan_path))
    pypi_projects = plan.get("pypi", plan["python"])
    versions = [version for version in PACKAGE_SPLIT_RE.split(python_versions.strip()) if version]
    if not versions:
        raise ValueError("at least one Python version is required")

    python_validation = {
        "include": [
            {
                "package": project["name"],
                "path": project["path"],
            }
            for project in plan["python"]
        ]
    }
    python_build = {
        "include": [
            {
                "package": project["name"],
                "path": project["path"],
                "artifact": f'python-dist-{project["name"].replace("_", "-")}',
            }
            for project in pypi_projects
        ]
    }
    values = {
        "has_python": "true" if plan["python"] else "false",
        "has_pypi": "true" if pypi_projects else "false",
        "python_validation_matrix": json.dumps(python_validation, separators=(",", ":")),
        "python_build_matrix": json.dumps(python_build, separators=(",", ":")),
    }
    if output is None:
        print(json.dumps(values, indent=2))
        return
    with output.open("a", encoding="utf-8") as out:
        for key, value in values.items():
            out.write(f"{key}={value}\n")


def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(args), flush=True)
    return subprocess.run(args, cwd=ROOT, check=True, text=True, **kwargs)


def git_output(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_config_value(key: str) -> str:
    result = subprocess.run(
        ["git", "config", key],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def ensure_git_identity() -> None:
    name = git_config_value("user.name")
    email = git_config_value("user.email")
    if name and email:
        return
    if not name:
        run(["git", "config", "user.name", "github-actions[bot]"])
    if not email:
        run(
            [
                "git",
                "config",
                "user.email",
                "41898282+github-actions[bot]@users.noreply.github.com",
            ]
        )


def normalize_python_project(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def url_exists(url: str) -> bool:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30):
            return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise RuntimeError(f"{url} lookup failed with HTTP {exc.code}") from exc


def validate_release_targets(plan_path: Path, *, github: bool, pypi: bool) -> None:
    plan = json.loads(read(plan_path))
    failures: list[str] = []

    if github:
        for release in plan["github_releases"]:
            tag = release["tag"]
            tag_exists = subprocess.run(
                ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if tag_exists.returncode == 0:
                failures.append(f"Git tag already exists: {tag}")
                continue
            release_exists = subprocess.run(
                ["gh", "release", "view", tag],
                cwd=ROOT,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if release_exists.returncode == 0:
                failures.append(f"GitHub release already exists: {tag}")

    if pypi:
        for release in plan.get("pypi", plan["python"]):
            project = normalize_python_project(release["name"])
            version = release["version"]
            url = f"https://pypi.org/pypi/{project}/{version}/json"
            if url_exists(url):
                failures.append(f"PyPI version already exists: {project} {version}")

    if failures:
        print("Release target validation failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    selected = []
    if github:
        selected.append("GitHub releases")
    if pypi:
        selected.append("PyPI")
    print(f"Release target validation passed for: {', '.join(selected) or 'none'}")


def create_github_releases(plan_path: Path) -> None:
    plan = json.loads(read(plan_path))
    ensure_git_identity()
    head = git_output(["rev-parse", "HEAD"])
    tags: list[str] = []
    for release in plan["github_releases"]:
        tag = release["tag"]
        existing = subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if existing.returncode == 0:
            raise RuntimeError(f"tag {tag} already exists")
        run(["git", "tag", "-a", tag, "-m", tag])
        tags.append(tag)
    if tags:
        run(["git", "push", "origin", *tags])

    for release in plan["github_releases"]:
        tag = release["tag"]
        title = tag
        is_prerelease = "dev" in tag
        body = (
            f'Automated {release["kind"]} release for `{release["name"]}`.\n\n'
            f'- version: `{release["version"]}`\n'
            f'- manifest: `{release["path"]}`\n'
            f'- semver action: `{plan["semver"]}`\n'
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as notes:
            notes.write(body)
            notes_path = notes.name
        try:
            existing = subprocess.run(
                ["gh", "release", "view", tag],
                cwd=ROOT,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if existing.returncode == 0:
                raise RuntimeError(f"GitHub release {tag} already exists")
            command = [
                "gh",
                "release",
                "create",
                tag,
                "--title",
                title,
                "--notes-file",
                notes_path,
                "--target",
                head,
            ]
            if is_prerelease or plan["prerelease"]:
                command.append("--prerelease")
            run(command)
        finally:
            Path(notes_path).unlink(missing_ok=True)


def build_pypi_packages(plan_path: Path, *, out_dir: str) -> None:
    plan = json.loads(read(plan_path))
    projects = plan.get("pypi", plan["python"])
    if not projects:
        raise RuntimeError("release plan does not include any Python packages")
    for project in projects:
        run(["uv", "build", "--package", project["name"], "--out-dir", out_dir])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    bump = subparsers.add_parser("bump")
    bump.add_argument(
        "--semver",
        choices=["minor", "patch", "dev", "x", "y", "z", "finalize"],
        required=True,
        help=(
            "Canonical bump names are minor, patch, and dev for "
            "w.x.y.devZ workflow versions; "
            "finalize removes the dev suffix. "
            "Legacy aliases x/y/z are also accepted."
        ),
    )
    bump.add_argument("--summary", type=Path, required=True)
    bump.add_argument(
        "--packages",
        default="all",
        help="Comma- or whitespace-separated package names to include, or 'all'.",
    )
    bump.add_argument("--write", action="store_true")

    matrices = subparsers.add_parser("github-matrices")
    matrices.add_argument("--summary", type=Path, required=True)
    matrices.add_argument(
        "--python-versions",
        default="3.10,3.11,3.12,3.13,3.14",
        help="Comma- or whitespace-separated Python versions for validation.",
    )
    matrices.add_argument("--github-output", type=Path)

    gh = subparsers.add_parser("create-github-releases")
    gh.add_argument("--summary", type=Path, required=True)

    validate_targets = subparsers.add_parser("validate-release-targets")
    validate_targets.add_argument("--summary", type=Path, required=True)
    validate_targets.add_argument("--github", action="store_true")
    validate_targets.add_argument("--pypi", action="store_true")

    pypi = subparsers.add_parser("build-pypi-packages")
    pypi.add_argument("--summary", type=Path, required=True)
    pypi.add_argument("--out-dir", default="dist")

    args = parser.parse_args(argv)

    if args.command == "bump":
        plan = build_plan(args.semver, write_changes=args.write, packages=args.packages)
        args.summary.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(plan, indent=2))
        return 0
    if args.command == "github-matrices":
        matrix_output(
            args.summary,
            python_versions=args.python_versions,
            output=args.github_output,
        )
        return 0
    if args.command == "create-github-releases":
        if not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
            raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is required")
        create_github_releases(args.summary)
        return 0
    if args.command == "validate-release-targets":
        if args.github and not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
            raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is required")
        validate_release_targets(
            args.summary,
            github=args.github,
            pypi=args.pypi,
        )
        return 0
    if args.command == "build-pypi-packages":
        build_pypi_packages(args.summary, out_dir=args.out_dir)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
