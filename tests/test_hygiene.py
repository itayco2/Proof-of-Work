"""No internal labels or placeholders leak into public docs; icons are 512 square; the results table has its shape."""
import re

import pytest

from tests.conftest import EXPECTED, PUBLIC_MD, ROOT, project_dirs, read, rel

FORBIDDEN = ["TODO", "TBD", "RAW", "AGENT", "UNVERIFIED"]


@pytest.mark.parametrize("f", PUBLIC_MD, ids=[rel(p) for p in PUBLIC_MD])
def test_no_internal_labels_or_placeholders(f):
    text = read(f)
    for word in FORBIDDEN:
        assert not re.search(rf"\b{word}\b", text), f"{rel(f)} contains {word}"


@pytest.mark.parametrize("d", project_dirs(), ids=EXPECTED)
def test_icon_png_is_512_square(d):
    data = (d / "icon.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    assert (w, h) == (512, 512), f"icon.png is {w}x{h}, not 512x512"


def test_results_table_has_five_columns():
    rows = [line for line in read(ROOT / "RESULTS.md").splitlines() if line.startswith("|")]
    assert len(rows) >= 2, "RESULTS.md needs a header row and a separator row"
    for row in rows:
        assert row.count("|") == 6, f"this row does not have five columns: {row}"
