"""THE GATE. Under a minute, before anything else.

1. The fast tier (tests/): the contracts every guide and prompt must meet. Under a second.
2. Every external link in the public docs, checked live. 404 and 410 fail. A refusal (403, 405,
   429) or a timeout is reported and skipped, because a site that blocks scripts is not a dead source.

Run:  python scripts/gate.py               both
      python scripts/gate.py --no-links    the fast tier only
      python scripts/gate.py --links-only  the link check only (what CI runs weekly)
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
# Present as a desktop browser: a reasonable default for a script that fetches public pages, and
# Accept / Accept-Language are simply what a browser sends. It is not what fixed the false dead
# links here, and no site in these docs was found to gate on the User-Agent. The real cause is the
# method: some servers answer HEAD with 404 while serving the same page fine on GET, so probe()
# retries a HEAD 404 with GET rather than trusting it.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
SKIP_STATUSES = {403, 405, 429}
DEAD_STATUSES = {404, 410}


def public_md() -> list[Path]:
    return sorted(ROOT.glob("*.md")) + sorted((ROOT / "projects").glob("*/*.md"))


def urls() -> list[str]:
    found = set()
    for f in public_md():
        for u in URL.findall(f.read_text(encoding="utf-8")):
            found.add(u.rstrip(".,;:!?)"))
    return sorted(found)


def probe(url: str, timeout: float = 8.0):
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 404, 405):
                continue
            return e.code
        except Exception as e:  # timeouts, DNS, TLS
            return type(e).__name__
    return "no response"


def fast_tier() -> int:
    started = time.time()
    code = subprocess.call([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT)
    print(f"fast tier: {'ok' if code == 0 else 'FAIL'} in {time.time() - started:.2f}s")
    return code


def links() -> int:
    started = time.time()
    found = urls()
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(probe, found))
    dead = [(u, s) for u, s in zip(found, results) if s in DEAD_STATUSES]
    skipped = [(u, s) for u, s in zip(found, results) if not isinstance(s, int) or s in SKIP_STATUSES]
    for u, s in dead:
        print(f"[ FAIL ] {s} {u}")
    for u, s in skipped:
        print(f"[ skip ] {s} {u}")
    print(f"links: {len(found)} checked, {len(dead)} dead, {len(skipped)} skipped, {time.time() - started:.1f}s")
    return 1 if dead else 0


def main(argv: list[str]) -> int:
    code = 0
    if "--links-only" not in argv:
        code |= fast_tier()
    if "--no-links" not in argv:
        code |= links()
    print("gate:", "PASS" if code == 0 else "FAIL")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
