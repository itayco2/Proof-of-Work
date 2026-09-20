"""Every project folder exists, with its four files, and the README points at each one."""
import pytest

from tests.conftest import EXPECTED, PROJECTS, ROOT, project_dirs, read


def test_exactly_five_projects():
    found = sorted(p.name for p in PROJECTS.iterdir() if p.is_dir()) if PROJECTS.exists() else []
    assert found == EXPECTED


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_four_files(d):
    for name in ["README.md", "PROMPT.md", "icon.svg", "icon.png"]:
        assert (d / name).exists(), f"{d.name} is missing {name}"
    present = sorted(p.name for p in d.iterdir() if not p.name.startswith(".")) if d.exists() else []
    assert set(present) <= {"README.md", "PROMPT.md", "icon.svg", "icon.png"}, f"{d.name} has extra files: {present}"


def test_root_readme_links_every_project():
    readme = read(ROOT / "README.md")
    for name in EXPECTED:
        assert f"projects/{name}/" in readme, f"README does not link projects/{name}/"
