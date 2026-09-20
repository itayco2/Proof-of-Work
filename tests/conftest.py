"""Shared paths and helpers for the fast tier. Stdlib only; no network; no model."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"
EXPECTED = ["01-fixer", "02-scholar", "03-concierge", "04-librarian", "05-david"]

GUIDE_HEADINGS = [
    "What you build",
    "Why it gets interviews",
    "How it works",
    "The numbers",
    "Free and local",
    "Time and money",
    "What to publish",
    "Interview questions it answers",
    "Sources",
]
PROMPT_HEADINGS = [
    "Goal",
    "Interview me first",
    "Provider abstraction",
    "Phases",
    "Credibility layer",
    "Out of scope",
    "Rules",
    "Final verification",
]

PUBLIC_MD = sorted(ROOT.glob("*.md")) + sorted(PROJECTS.glob("*/*.md"))


def project_dirs() -> list[Path]:
    return [PROJECTS / name for name in EXPECTED]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def h2s(text: str) -> list[str]:
    """The `## ` headings of a markdown file, in order."""
    return [m.group(1).strip() for m in re.finditer(r"^## (.+?)\s*$", text, re.M)]


def section(text: str, heading: str) -> str:
    """The body of one `## heading`, up to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert m, f"missing section: {heading}"
    return m.group(1)


def words(text: str) -> int:
    return len(text.split())


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))
