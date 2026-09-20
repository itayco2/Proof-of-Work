"""Every relative link and image in the public docs points at a file that exists."""
import re

import pytest

from tests.conftest import PUBLIC_MD, read, rel

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HTML_SRC = re.compile(r'src="([^"]+)"')


@pytest.mark.parametrize("f", PUBLIC_MD, ids=[rel(p) for p in PUBLIC_MD])
def test_relative_links_resolve(f):
    text = read(f)
    for target in LINK.findall(text) + HTML_SRC.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path = (f.parent / target.split("#")[0]).resolve()
        assert path.exists(), f"{rel(f)} links to {target}, which does not exist"
