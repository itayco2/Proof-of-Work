"""The README thumbnails and the social-preview banner, built from the five illustrations. Stdlib only.

The source of truth is each project's icon: projects/NN-name/icon.png, a 512 px illustration of the
project's story (generated with Google Gemini). This script derives two things from those five files:

  assets/<name>-128.png   the thumbnails in the README table
  assets/banner.png       the 1280 by 640 social preview, set on GitHub under Settings

Run it after replacing an illustration:

  CHROME_BIN="$HOME/Desktop/Google Chrome.app/Contents/MacOS/Google Chrome" python scripts/make_icons.py

Headless Chrome renders each image from a small HTML page. Chrome is given 20 seconds and the expiry is
expected: on some machines it writes the screenshot at once and then never exits. It hangs on a Keychain
prompt unless launched with --use-mock-keychain and an isolated --user-data-dir, never a real profile.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER, INK, MUTE = "#f3efe6", "#141413", "#7a766c"

# folder, thumbnail name, accent (the shadow colour on the banner)
PROJECTS = [
    ("01-the-night-shift", "the-night-shift", "#f5a623"),
    ("02-citation-needed", "citation-needed", "#8b7cf6"),
    ("03-hello-world", "hello-world", "#2dd4bf"),
    ("04-needle-in-a-haystack", "needle-in-a-haystack", "#4f9cf9"),
    ("05-david-vs-goliath", "david-vs-goliath", "#ef476f"),
]
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800'
         '&family=IBM+Plex+Mono:wght@400;500&display=swap">')


def icon(folder: str) -> Path:
    return ROOT / "projects" / folder / "icon.png"


def thumbnail_html(folder: str) -> str:
    return (f'<!doctype html><html><body style="margin:0;background:{PAPER}">'
            f'<img src="{icon(folder).as_uri()}" style="display:block;width:128px;height:128px;border-radius:22px"></body></html>')


def banner_html() -> str:
    tiles = "".join(
        f'<img src="{icon(folder).as_uri()}" style="width:196px;height:196px;box-sizing:border-box;'
        f'border:3px solid {INK};border-radius:28px;box-shadow:8px 8px 0 {accent};object-fit:cover">'
        for folder, _, accent in PROJECTS)
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}</head>'
            f'<body style="margin:0;width:1280px;height:640px;overflow:hidden;background:{PAPER}">'
            '<div style="box-sizing:border-box;width:1280px;height:640px;padding:60px 72px;display:flex;flex-direction:column;gap:18px">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline">'
            f'<div style="font-family:\'Bricolage Grotesque\',\'Helvetica Neue\',sans-serif;font-weight:800;font-size:84px;'
            f'letter-spacing:-0.03em;line-height:1;color:{INK}">Proof of Work</div>'
            f'<div style="font-family:\'IBM Plex Mono\',Menlo,monospace;font-size:22px;color:{MUTE}">free · open source</div></div>'
            f'<div style="font-family:\'IBM Plex Mono\',Menlo,monospace;font-size:26px;color:{INK}">'
            'Five AI projects, each with the master prompt that builds it.</div>'
            f'<div style="margin-top:auto;display:flex;justify-content:space-between">{tiles}</div>'
            '</div></body></html>')


def render(html: str, out: Path, width: int, height: int, chrome: str, tmp: Path) -> None:
    page = tmp / (out.stem + ".html")
    page.write_text(html, encoding="utf-8")
    if out.exists():
        out.unlink()
    try:
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--no-default-browser-check", "--use-mock-keychain", "--password-store=basic",
             "--disable-extensions", "--disable-sync", "--allow-file-access-from-files",
             f"--user-data-dir={tmp / 'profile'}", "--force-device-scale-factor=1",
             "--virtual-time-budget=8000", f"--window-size={width},{height}",
             f"--screenshot={out}", page.as_uri()],
            capture_output=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        pass  # the screenshot is written before the hang; the checks below decide
    if not out.exists():
        raise SystemExit(f"{out}: Chrome wrote nothing; point CHROME_BIN at a working Chrome")
    data = out.read_bytes()
    w, h = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if (w, h) != (width, height):
        raise SystemExit(f"{out}: got {w}x{h}, wanted {width}x{height}")


def main() -> int:
    chrome = os.environ.get("CHROME_BIN")
    if not chrome:
        raise SystemExit("set CHROME_BIN to a Chrome binary")
    missing = [str(icon(f)) for f, _, _ in PROJECTS if not icon(f).exists()]
    if missing:
        raise SystemExit("missing illustrations: " + ", ".join(missing))
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="icons-") as tmpdir:
        tmp = Path(tmpdir)
        for folder, name, _ in PROJECTS:
            render(thumbnail_html(folder), assets / f"{name}-128.png", 128, 128, chrome, tmp)
            print(f"wrote assets/{name}-128.png")
        render(banner_html(), assets / "banner.png", 1280, 640, chrome, tmp)
        print("wrote assets/banner.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
