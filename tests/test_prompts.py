"""The master-prompt contract from design.md §6."""
import re

import pytest

from tests.conftest import EXPECTED, PROMPT_HEADINGS, h2s, project_dirs, read, section, words

LABELS = ["Do:", "Done when:", "Verify:", "Checkpoint:"]


def prompt(d):
    return read(d / "PROMPT.md")


def phases(text):
    return re.split(r"^### ", section(text, "Phases"), flags=re.M)[1:]


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_eight_blocks_in_order(d):
    assert h2s(prompt(d)) == PROMPT_HEADINGS


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_goal_ends_in_a_number(d):
    m = re.search(r"Done when:(.+)", section(prompt(d), "Goal"))
    assert m and re.search(r"\d", m.group(1)), "Goal needs a 'Done when:' line that names a number"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_interview_offers_both_paths(d):
    body = section(prompt(d), "Interview me first")
    assert "`api`" in body and "`local`" in body


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_at_least_four_phases_each_with_four_labels(d):
    ps = phases(prompt(d))
    assert len(ps) >= 4
    for p in ps:
        for label in LABELS:
            assert label in p, f"a phase lacks {label!r}: {p[:60]!r}"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_every_done_when_is_measurable(d):
    for p in phases(prompt(d)):
        m = re.search(r"Done when:(.+)", p)
        assert m and re.search(r"\d", m.group(1)), f"'Done when' without a number in: {p[:60]!r}"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_phase_one_is_the_skeleton(d):
    first = phases(prompt(d))[0]
    assert "Makefile" in first and "gate" in first.lower() and "test" in first.lower()


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_credibility_layer_names_its_artifacts(d):
    body = section(prompt(d), "Credibility layer")
    for needle in ["PREFLIGHT.md", "eval", "README", "recording"]:
        assert needle in body, f"credibility layer does not mention {needle}"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_out_of_scope_is_stated(d):
    assert words(section(prompt(d), "Out of scope")) >= 10


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_rules_cover_numbers_secrets_and_budget(d):
    body = section(prompt(d), "Rules").lower()
    assert "reproduc" in body and ".env" in body and "budget" in body


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_word_budget(d):
    n = words(prompt(d))
    assert 1200 <= n <= 2500, f"{d.name}/PROMPT.md has {n} words; the budget is 1,200 to 2,500"
