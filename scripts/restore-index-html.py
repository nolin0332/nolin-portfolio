#!/usr/bin/env python3
"""Fetch fresh index.html and inject julio-overrides block."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "public" / "index.html"
OVERRIDES = ROOT / "scripts" / "julio-overrides.css"
REF = "https://julio-modern.vercel.app/"


def main() -> None:
    print("Fetching", REF)
    html = urllib.request.urlopen(REF, timeout=120).read().decode("utf-8")
    if OVERRIDES.exists():
        css = OVERRIDES.read_text(encoding="utf-8").strip()
        html = re.sub(
            r"</script><style>/\* julio-overrides \*/.*?</style></head>",
            f"</script><style>/* julio-overrides */\n{css}\n</style></head>",
            html,
            count=1,
        )
        if "julio-overrides" not in html:
            html = html.replace(
                "</head>",
                f'<style>/* julio-overrides */\n{css}\n</style></head>',
                1,
            )
        print("Injected julio-overrides")
    INDEX.write_text(html, encoding="utf-8")
    print("Wrote", INDEX)


if __name__ == "__main__":
    main()
