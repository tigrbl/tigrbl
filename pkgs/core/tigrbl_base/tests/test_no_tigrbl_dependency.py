from pathlib import Path


def test_tigrbl_base_does_not_depend_on_tigrbl_package() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    dependencies: list[str] = []
    in_dependencies = False
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_dependencies = True
            continue
        if in_dependencies and stripped == "]":
            break
        if in_dependencies and stripped.startswith('"'):
            dependencies.append(stripped.strip('",'))

    assert "tigrbl" not in dependencies
    assert all(not dep.startswith("tigrbl==") for dep in dependencies)
