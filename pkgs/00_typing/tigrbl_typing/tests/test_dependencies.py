from pathlib import Path


def test_project_declares_expected_runtime_dependencies() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    dependencies: list[str] = []
    in_dependencies = False
    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_dependencies = True
            continue
        if in_dependencies and stripped == "]":
            break
        if in_dependencies and stripped.startswith('"'):
            dependencies.append(stripped.strip('",'))

    assert dependencies == ["pydantic>=2.10,<3"]
