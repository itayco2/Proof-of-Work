"""Every icon, from one style definition. Stdlib only.

SVG is the source (projects/NN-name/icon.svg). PNGs are exported with headless Chrome:

  CHROME_BIN="$HOME/Desktop/Google Chrome.app/Contents/MacOS/Google Chrome" python scripts/make_icons.py

Without CHROME_BIN the SVGs are still written and the PNG step is skipped with a note.
Chrome pitfalls already paid for elsewhere in this workspace: it hangs on a Keychain prompt
unless launched with --use-mock-keychain and an isolated --user-data-dir (never the real profile).
On this Mac, Chrome writes the screenshot at once and then never exits, so export_png gives it
20 seconds and treats the expiry itself as expected, trusting the file that is already on disk.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZE = 512
BG = "#0f1117"
INK = "#f4f4f5"
STROKE = 30

ACCENT = {
    "01-fixer": "#f5a623",
    "02-scholar": "#8b7cf6",
    "03-concierge": "#2dd4bf",
    "04-librarian": "#4f9cf9",
    "05-david": "#ef476f",
}
SHORT = {name: name.split("-", 1)[1] for name in ACCENT}


def stroke(color: str, width: int = STROKE) -> str:
    return f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'


def fixer(a: str) -> str:
    # a pull-request mark in ink; a wrench (open ring + handle) crossing in from the right, in the accent
    return f"""
  <g {stroke(INK)}>
    <circle cx="140" cy="126" r="34"/>
    <circle cx="140" cy="386" r="34"/>
    <path d="M140 160 V352"/>
    <path d="M214 126 H262 Q306 126 306 170 V236"/>
  </g>
  <g {stroke(a)}>
    <circle cx="384" cy="250" r="50" stroke-dasharray="230 84" transform="rotate(-30 384 250)"/>
    <path d="M356 288 L236 408"/>
  </g>"""


def scholar(a: str) -> str:
    # an open book in ink; a citation bracket pair in the accent, top right
    return f"""
  <g {stroke(INK)}>
    <path d="M256 168 Q176 130 96 166 V386 Q176 350 256 388 Z"/>
    <path d="M256 168 Q336 130 416 166 V386 Q336 350 256 388 Z"/>
    <path d="M256 168 V388"/>
  </g>
  <g {stroke(a, 22)}>
    <path d="M356 74 H332 V138 H356"/>
    <path d="M404 74 H428 V138 H404"/>
    <circle cx="380" cy="106" r="7" fill="{a}" stroke="none"/>
  </g>"""


def concierge(a: str) -> str:
    # a bell in ink; a sound wave underneath in the accent
    return f"""
  <g {stroke(INK)}>
    <path d="M256 104 C190 104 166 160 166 224 V292 H346 V224 C346 160 322 104 256 104 Z"/>
    <circle cx="256" cy="90" r="14" fill="{INK}" stroke="none"/>
    <path d="M226 326 Q256 352 286 326"/>
  </g>
  <g {stroke(a, 26)}>
    <path d="M96 420 q32 -48 64 0 t64 0 t64 0 t64 0 t64 0"/>
  </g>"""


def librarian(a: str) -> str:
    # three book spines in ink; a magnifier in the accent
    return f"""
  <g {stroke(INK)}>
    <rect x="96" y="152" width="58" height="256" rx="14"/>
    <rect x="176" y="112" width="58" height="296" rx="14"/>
    <rect x="256" y="176" width="58" height="232" rx="14"/>
  </g>
  <g {stroke(a)}>
    <circle cx="384" cy="228" r="52"/>
    <path d="M422 266 L462 306"/>
  </g>"""


def david(a: str) -> str:
    # Goliath: a large outlined square in the accent; David: a small filled stone in ink, with its sling
    return f"""
  <g {stroke(a)}>
    <rect x="268" y="104" width="172" height="172" rx="30"/>
  </g>
  <g {stroke(INK)}>
    <path d="M78 428 Q98 322 152 322"/>
    <circle cx="164" cy="322" r="26" fill="{INK}" stroke="none"/>
    <path d="M214 300 L246 268" stroke-dasharray="8 22"/>
  </g>"""


GLYPHS = {"01-fixer": fixer, "02-scholar": scholar, "03-concierge": concierge, "04-librarian": librarian, "05-david": david}


def icon_svg(name: str) -> str:
    a = ACCENT[name]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
  <rect width="{SIZE}" height="{SIZE}" rx="96" fill="{BG}"/>
  <rect x="9" y="9" width="{SIZE - 18}" height="{SIZE - 18}" rx="88" fill="none" stroke="{a}" stroke-opacity="0.35" stroke-width="6"/>{GLYPHS[name](a)}
</svg>
"""


def banner_svg() -> str:
    tiles = []
    for i, name in enumerate(ACCENT):
        x = 88 + i * 224
        inner = icon_svg(name).split("\n", 1)[1].rsplit("</svg>", 1)[0]
        tiles.append(f'<g transform="translate({x} 120) scale(0.3125)">{inner}</g>')
    font = "-apple-system, 'Helvetica Neue', Arial, sans-serif"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" width="1280" height="640">
  <rect width="1280" height="640" fill="{BG}"/>
  {''.join(tiles)}
  <text x="640" y="380" text-anchor="middle" font-family="{font}" font-size="64" font-weight="700" fill="{INK}">five-ai-projects</text>
  <text x="640" y="440" text-anchor="middle" font-family="{font}" font-size="30" fill="#a1a1aa">Five portfolio projects that make an AI engineer's GitHub say "you built that?"</text>
  <text x="640" y="490" text-anchor="middle" font-family="{font}" font-size="26" fill="#71717a">a guide and a Claude Code master prompt for each · runs on an API or fully local and free</text>
</svg>
"""


def sized(svg: str, width: int, height: int) -> str:
    """The same SVG with the root element's width and height set (the viewBox does the scaling)."""
    return re.sub(r'width="\d+" height="\d+"', f'width="{width}" height="{height}"', svg, count=1)


def export_png(svg: str, out: Path, width: int, height: int, chrome: str, tmp: Path) -> None:
    html = tmp / (out.stem + ".html")
    html.write_text(
        f'<!doctype html><html><body style="margin:0;background:transparent">{sized(svg, width, height)}</body></html>',
        encoding="utf-8",
    )
    if out.exists():
        out.unlink()
    try:
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--no-default-browser-check", "--use-mock-keychain", "--password-store=basic",
             "--disable-extensions", "--disable-background-networking", "--disable-sync",
             f"--user-data-dir={tmp / 'profile'}", "--force-device-scale-factor=1",
             "--default-background-color=00000000", f"--window-size={width},{height}",
             f"--screenshot={out}", f"file://{html}"],
            capture_output=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        pass  # Chrome on this Mac writes the screenshot at once and then never exits; the file is what matters
    if not out.exists():
        raise SystemExit(f"{out}: Chrome wrote nothing; run with CHROME_BIN pointing at a working Chrome")
    data = out.read_bytes()
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    if (w, h) != (width, height):
        raise SystemExit(f"{out}: got {w}x{h}, wanted {width}x{height}")


def main() -> int:
    chrome = os.environ.get("CHROME_BIN")
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="icons-") as tmpdir:
        tmp = Path(tmpdir)
        for name in ACCENT:
            folder = ROOT / "projects" / name
            folder.mkdir(parents=True, exist_ok=True)
            svg = icon_svg(name)
            (folder / "icon.svg").write_text(svg, encoding="utf-8")
            print(f"wrote projects/{name}/icon.svg")
            if chrome:
                export_png(svg, folder / "icon.png", SIZE, SIZE, chrome, tmp)
                export_png(svg, assets / f"{SHORT[name]}-128.png", 128, 128, chrome, tmp)
                print(f"wrote projects/{name}/icon.png and assets/{SHORT[name]}-128.png")
        banner = banner_svg()
        (assets / "banner.svg").write_text(banner, encoding="utf-8")
        if chrome:
            export_png(banner, assets / "banner.png", 1280, 640, chrome, tmp)
            print("wrote assets/banner.png")
        else:
            print("CHROME_BIN not set: SVGs written, PNG export skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
