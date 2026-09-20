"""The guide contract from design.md §5."""
import re

import pytest

from tests.conftest import EXPECTED, GUIDE_HEADINGS, h2s, project_dirs, read, section, words


def guide(d):
    return read(d / "README.md")


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_nine_sections_in_order(d):
    assert h2s(guide(d)) == GUIDE_HEADINGS


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_opens_with_its_icon(d):
    first = next(line for line in guide(d).splitlines() if line.strip())
    assert first.startswith("![") and "icon.png" in first, "the guide must open with ![... icon](icon.png)"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_word_budget(d):
    n = words(guide(d))
    assert 700 <= n <= 1800, f"{d.name}/README.md has {n} words; the budget is 700 to 1,800"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_sources_carry_urls(d):
    assert len(re.findall(r"https?://", section(guide(d), "Sources"))) >= 3


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_five_interview_questions(d):
    body = section(guide(d), "Interview questions it answers")
    assert len(re.findall(r"^\d+\. ", body, re.M)) == 5


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_numbers_section_has_numbers(d):
    assert re.search(r"\d", section(guide(d), "The numbers"))


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_free_and_local_names_a_free_runtime(d):
    body = section(guide(d), "Free and local").lower()
    assert "ollama" in body or "colab" in body or "mlx" in body
