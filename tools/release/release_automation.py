from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_VERSION_RE = re.compile(r'(?m)^(version\s*=\s*)"([^"]+)"')
CARGO_WORKSPACE_VERSION_RE = re.compile(
    r'(?ms)^(\[workspace\.package\].*?^version\s*=\s*)"([^"]+)"'
)
CARGO_PACKAGE_NAME_RE = re.compile(r'(?m)^name\s*=\s*"([^"]+)"')
CARGO_DEP_RE = re.compile(r'^(\s*)([A-Za-z0-9_-]+)\s*=\s*\{([^}]*)\}(\s*)$')
PACKAGE_SPLIT_RE = re.compile(r"[\s,]+")


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    dev: int | None = None
    cargo: bool = False

    @classmethod
    def parse(cls, value: str, *, cargo: bool = False) -> "Version":
        if cargo:
            match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-dev\.(\d+))?", value)
        else:
            match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:\.dev(\d+))?", value)
        if not match:
            raise ValueError(f"unsupported version {value!r}")
        major, minor, patch, dev = match.groups()
        return cls(
            int(major),
            int(minor),
            int(patch),
            int(dev) if dev is not None else None,
            cargo=cargo,
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
            return Version(self.major, self.minor, self.patch, cargo=self.cargo)
        if segment == "minor":
            return Version(self.major, self.minor + 1, 0, 1, self.cargo)
        if segment in {"patch", "dev"}:
            if self.dev is None:
                return Version(self.major, self.minor, self.patch + 1, 1, self.cargo)
            return Version(self.major, self.minor, self.patch, self.dev + 1, self.cargo)
        raise ValueError(f"unsupported semver bump action {semver!r}")

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.dev is None:
            return base
        if self.cargo:
            return f"{base}-dev.{self.dev}"
        return f"{base}.dev{self.dev}"


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


def cargo_members() -> list[Path]:
    root_manifest = read(ROOT / "Cargo.toml")
    members_match = re.search(r"(?ms)^members\s*=\s*\[(.*?)\]", root_manifest)
    if not members_match:
        raise RuntimeError("Cargo workspace members were not found")
    members: list[Path] = []
    for member in re.findall(r'"([^"]+)"', members_match.group(1)):
        members.append(ROOT / member / "Cargo.toml")
    return members


def cargo_workspace_version() -> str:
    match = CARGO_WORKSPACE_VERSION_RE.search(read(ROOT / "Cargo.toml"))
    if not match:
        raise RuntimeError("Cargo workspace package version was not found")
    return match.group(2)


def cargo_projects() -> list[dict[str, str]]:
    version = cargo_workspace_version()
    projects: list[dict[str, str]] = []
    for manifest in cargo_members():
        text = read(manifest)
        name_match = CARGO_PACKAGE_NAME_RE.search(text)
        if not name_match:
            raise RuntimeError(f"Cargo package name not found in {manifest}")
        projects.append(
            {"name": name_match.group(1), "version": version, "path": relative(manifest)}
        )
    return projects


def cargo_publish_order(projects: Iterable[dict[str, str]]) -> list[str]:
    preferred = [
        "tigrbl_rs_spec",
        "tigrbl_rs_ports",
        "tigrbl_rs_ops_olap",
        "tigrbl_rs_ops_realtime",
        "tigrbl_rs_engine_sqlite",
        "tigrbl_rs_engine_postgres",
        "tigrbl_rs_engine_inmemory",
        "tigrbl_rs_atoms",
        "tigrbl_rs_ops_oltp",
        "tigrbl_rs_kernel",
        "tigrbl_rs_runtime",
        "tigrbl_runtime_bindings",
    ]
    names = {project["name"] for project in projects}
    missing = names.difference(preferred)
    if missing:
        raise RuntimeError(f"missing Cargo publish order entries: {sorted(missing)}")
    return [name for name in preferred if name in names]


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
    cargo: list[dict[str, str]],
) -> None:
    if selected is None:
        return
    known = {project["name"] for project in [*py_projects, *cargo]}
    unknown = selected.difference(known)
    if unknown:
        known_list = ", ".join(sorted(known))
        unknown_list = ", ".join(sorted(unknown))
        raise ValueError(f"unknown package(s): {unknown_list}. Known packages: {known_list}")


def replace_python_version(path: Path, new_version: str) -> bool:
    text = read(path)
    updated, count = PYPROJECT_VERSION_RE.subn(rf'\g<1>"{new_version}"', text, count=1)
    if count != 1:
        raise RuntimeError(f"project version not found in {path}")
    return write_if_changed(path, updated)


def replace_cargo_workspace_version(new_version: str) -> bool:
    path = ROOT / "Cargo.toml"
    text = read(path)
    updated, count = CARGO_WORKSPACE_VERSION_RE.subn(
        rf'\g<1>"{new_version}"', text, count=1
    )
    if count != 1:
        raise RuntimeError("Cargo workspace package version was not updated")
    return write_if_changed(path, updated)


def update_cargo_internal_dependency_versions(
    manifests: Iterable[Path], internal_names: set[str], new_version: str
) -> list[str]:
    changed: list[str] = []
    for manifest in manifests:
        lines = read(manifest).splitlines(keepends=True)
        next_lines: list[str] = []
        touched = False
        for line in lines:
            line_ending = "\n" if line.endswith("\n") else ""
            content = line[:-1] if line_ending else line
            match = CARGO_DEP_RE.match(content)
            if not match or match.group(2) not in internal_names or "path" not in match.group(3):
                next_lines.append(line)
                continue
            indent, dep_name, body, trailing = match.groups()
            if re.search(r'\bversion\s*=', body):
                body = re.sub(r'\bversion\s*=\s*"[^"]+"', f'version = "{new_version}"', body)
            else:
                body = f'{body.rstrip()}, version = "{new_version}"'
            next_lines.append(f"{indent}{dep_name} = {{{body}}}{trailing}{line_ending}")
            touched = True
        if touched and write_if_changed(manifest, "".join(next_lines)):
            changed.append(relative(manifest))
    return changed


def build_plan(
    semver: str, *, write_changes: bool, packages: str | None = None
) -> dict[str, object]:
    all_py_projects = python_projects()
    all_cargo = cargo_projects()
    selected = parse_package_selection(packages)
    validate_package_selection(selected, all_py_projects, all_cargo)
    py_projects = filter_projects(all_py_projects, selected)
    cargo = filter_projects(all_cargo, selected)
    changed: list[str] = []

    py_releases: list[dict[str, str]] = []
    for project in py_projects:
        new_version = str(Version.parse(project["version"]).bump(semver))
        py_releases.append({**project, "old_version": project["version"], "version": new_version})
        if write_changes and replace_python_version(ROOT / project["path"], new_version):
            changed.append(project["path"])

    cargo_releases: list[dict[str, str]] = []
    if cargo:
        cargo_old_version = cargo_workspace_version()
        cargo_new_version = str(Version.parse(cargo_old_version, cargo=True).bump(semver))
        cargo_releases = [
            {**project, "old_version": cargo_old_version, "version": cargo_new_version}
            for project in cargo
        ]
        if write_changes and replace_cargo_workspace_version(cargo_new_version):
            changed.append("Cargo.toml")
        if write_changes:
            changed.extend(
                update_cargo_internal_dependency_versions(
                    cargo_members(),
                    {project["name"] for project in all_cargo},
                    cargo_new_version,
                )
            )

    all_releases = [
        {"kind": "pypi", "tag": f'{release["name"]}=={release["version"]}', **release}
        for release in py_releases
    ] + [
        {"kind": "crate", "tag": f'{release["name"]}=={release["version"]}', **release}
        for release in cargo_releases
    ]

    is_prerelease = any(
        Version.parse(release["version"], cargo=release["kind"] == "crate").dev is not None
        for release in all_releases
    )

    return {
        "semver": semver,
        "prerelease": is_prerelease,
        "package_selection": sorted(selected) if selected is not None else "all",
        "python": py_releases,
        "crates": cargo_releases,
        "crate_publish_order": cargo_publish_order(cargo_releases),
        "github_releases": all_releases,
        "changed_files": sorted(set(changed)),
    }


def matrix_output(plan_path: Path, *, python_versions: str, output: Path | None) -> None:
    plan = json.loads(read(plan_path))
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
            for project in plan["python"]
        ]
    }
    values = {
        "has_python": "true" if plan["python"] else "false",
        "has_crates": "true" if plan["crates"] else "false",
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
            tagged_head = git_output(["rev-list", "-n", "1", tag])
            if tagged_head != head:
                raise RuntimeError(f"tag {tag} already exists on {tagged_head}, not {head}")
        else:
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
                command = ["gh", "release", "edit", tag, "--title", title, "--notes-file", notes_path]
                if is_prerelease or plan["prerelease"]:
                    command.append("--prerelease")
                run(command)
            else:
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


def publish_crates(plan_path: Path, *, dry_run: bool, verify: bool = True) -> None:
    plan = json.loads(read(plan_path))
    if not plan["crate_publish_order"]:
        raise RuntimeError("release plan does not include any Rust crates")
    versions = {crate["name"]: crate["version"] for crate in plan["crates"]}
    packaged_locally: list[str] = []
    for crate in plan["crate_publish_order"]:
        patch_args: list[str] = []
        for packaged in packaged_locally:
            package_dir = ROOT / "target" / "package" / f"{packaged}-{versions[packaged]}"
            patch_args.extend(
                [
                    "--config",
                    f'patch.crates-io.{packaged}.path="{package_dir.as_posix()}"',
                ]
            )
        package_command = ["cargo", "package", "-p", crate, "--locked", *patch_args]
        publish_command = ["cargo", "publish", "-p", crate, "--locked"]
        if dry_run:
            run(package_command)
            packaged_locally.append(crate)
            continue
        if verify:
            run(package_command)
        run(publish_command)
        packaged_locally.append(crate)
        time.sleep(20)


def build_pypi_packages(plan_path: Path, *, out_dir: str) -> None:
    plan = json.loads(read(plan_path))
    if not plan["python"]:
        raise RuntimeError("release plan does not include any Python packages")
    for project in plan["python"]:
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
        default="3.10,3.11,3.12,3.13",
        help="Comma- or whitespace-separated Python versions for validation.",
    )
    matrices.add_argument("--github-output", type=Path)

    gh = subparsers.add_parser("create-github-releases")
    gh.add_argument("--summary", type=Path, required=True)

    crates = subparsers.add_parser("publish-crates")
    crates.add_argument("--summary", type=Path, required=True)
    crates.add_argument("--dry-run", action="store_true")
    crates.add_argument("--skip-dry-run", action="store_true")

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
    if args.command == "publish-crates":
        publish_crates(args.summary, dry_run=args.dry_run, verify=not args.skip_dry_run)
        return 0
    if args.command == "build-pypi-packages":
        build_pypi_packages(args.summary, out_dir=args.out_dir)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
